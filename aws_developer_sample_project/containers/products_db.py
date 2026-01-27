import boto3
import boto3.dynamodb.conditions
import uuid
from decimal import Decimal
import os
table_name=os.environ.get('PRODUCTS_TABLE_NAME') or 'Products'
table=boto3.resource('dynamodb').Table(table_name)

def get_product(product_id):
   return table.get_item(Key={'id': product_id}).get('Item')

def upsert_product(product_id, fields):
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
    
def insert_product(item):
   return upsert_product(str(uuid.uuid4()), item)

def delete_product(product_id):
   return table.delete_item(Key={'id': product_id}).get('Item')

def update_product(product_id, item):
   return upsert_product(product_id, item)

def get_all_products():
   return table.scan()['Items']

def get_products_by_category(category):
   return table.query(IndexName='category-index', KeyConditionExpression=boto3.dynamodb.conditions.Key('category').eq(category)).get('Items') 
