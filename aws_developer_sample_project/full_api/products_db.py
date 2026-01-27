import boto3
import boto3.dynamodb.conditions
import uuid
from decimal import Decimal
import redis
import json
import os
import urllib.request

table_name=os.environ.get('PRODUCTS_TABLE_NAME') or 'Products'
table=boto3.resource('dynamodb').Table(table_name)

def decimal_serializer(obj):
    """Handle Decimal objects in JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


cluster_url = os.environ['CACHE_CLUSTER_URL']
print(f"Cluster URL: {cluster_url}")

# Initialize Redis/Valkey connection (Redis-compatible)
if cluster_url:
   cache_client = redis.Redis(
      host=cluster_url,
      port=6379,
      decode_responses=True,
      ssl=True,
      socket_connect_timeout=5,
      socket_timeout=5
   )

# same as get_product from core_api
def get_product_from_dynamodb(product_id):
   return table.get_item(Key={'id': product_id}).get('Item')

# checks the cache first
def get_product(product_id):
   if not cluster_url:
      return get_product_from_dynamodb(product_id)
   cache_key = f"product:{product_id}"
   try:
      # Try cache first
      cached_product = cache_client.get(cache_key)
      print(f"{cached_product=}")
      if cached_product:
         print(f"Cache hit for product {product_id}")
         return json.loads(cached_product)
            
      # Cache miss - get from DynamoDB
      print(f"Cache miss for product {product_id}. Trying to get from dynamo")
      product = get_product_from_dynamodb(product_id)
      print(f"Got from dynamodb {product}")
      
      if product:
         product_str=json.dumps(product,default=decimal_serializer)
         print(f"{product_str=}")
         # Store in cache with 1 hour TTL
         cache_client.setex(cache_key, 3600, product_str)
         print(f"Stored {product_id}")
      
      return product
      
   except BaseException as e:
      print(f"Valkey error: {e}")
      # Fallback to database if cache fails
      return get_product_from_dynamodb(product_id)


def upsert_product_dynamo(product_id, fields):
   category=fields.get('category') or []
   title=fields.get('title') or ''
   description=fields.get('description') or ''
   price=Decimal(fields.get('price') or 0)

   update_expression = """
      SET category = :category,
      title = :title,
      description = :description,
      price = :price
   """
   expression_attribute_values = {
      ':category': category,
      ':title': title,
      ':description': description,
      ':price': price
   }
   inserted=table.update_item(
      Key={'id': product_id},
      UpdateExpression=update_expression,
      ExpressionAttributeValues=expression_attribute_values,
      ReturnValues="ALL_NEW"
   )
   return inserted['Attributes']

def update_price_dynamo(product_id, price):
   update_expression = """
      SET 
      price = :price
   """
   expression_attribute_values = {
      ':price': price
   }
   inserted=table.update_item(
      Key={'id': product_id},
      UpdateExpression=update_expression,
      ExpressionAttributeValues=expression_attribute_values,
      ReturnValues="ALL_NEW"
   )
   return inserted['Attributes']

def update_price(product_id,price):
   upserted=update_price_dynamo(product_id,price)
   if cluster_url:
      cache_key = f"product:{product_id}"
      cache_client.setex(cache_key, 3600, json.dumps(upserted, default=decimal_serializer))
   return upserted

def upsert_product(product_id, fields):
   if not cluster_url:
      return upsert_product_dynamo(product_id,fields)

   cache_key = f"product:{product_id}"
   print(f"Upserting product {product_id=}")   
   upserted=None
   upserted=upsert_product_dynamo(product_id,fields)
   cache_client.setex(cache_key, 3600, json.dumps(upserted, default=decimal_serializer))
   return upserted 
  
def insert_product(item):
   return upsert_product(str(uuid.uuid4()), item)

def delete_product(product_id):
   if cluster_url:
      cache_client.delete(f"product:{product_id}") # no need for checking
   return table.delete_item(Key={'id': product_id}).get('Item')

def update_product(product_id, item):
   return upsert_product(product_id, item)

def get_all_products():
   return table.scan()['Items']

def get_products_by_category(category):
   return table.query(IndexName='category-index', KeyConditionExpression=boto3.dynamodb.conditions.Key('category').eq(category)).get('Items') 
