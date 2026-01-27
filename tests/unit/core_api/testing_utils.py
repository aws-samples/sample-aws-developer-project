import os
import sys
import boto3
from decimal import Decimal

folder_to_add = os.path.abspath('aws_developer_sample_project/core_api') 

class Expando(object):
    pass

def load_path(cls):
   if folder_to_add in sys.path:
      return cls
   original_setUp=cls.setUp
   original_tearDown=cls.tearDown
   def setUp(self):
      sys.path.append(folder_to_add)
      original_setUp(self)
   def tearDown(self):
      original_tearDown(self)
      sys.path.remove(folder_to_add)
   cls.setUp = setUp
   cls.tearDown = tearDown
   return cls

sample_products = [
   {
      'id': '1',
      'title': 'Product 1',
      'description': 'Product 1 description',
      'price': 10,
      'category': 'category1'
   },
   {
      'id': '2',
      'title': 'Product 2',
      'description': 'Product 2 description',
      'price': 20,
      'category': 'category2'
   }
]
table_name = "Products"

def create_resources(products_db):
      dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
      table=dynamodb.create_table(
         TableName = table_name,
         KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
         AttributeDefinitions=[
            {"AttributeName": "id", "AttributeType": "S"},
            {"AttributeName": "category", "AttributeType": "S"},
         ],
         BillingMode='PAY_PER_REQUEST',
         GlobalSecondaryIndexes=[
            {
               'IndexName': 'category-index',
               'KeySchema': [
                  {'AttributeName': 'category', 'KeyType': 'HASH'} # GSI Partition key
               ],
               'Projection': {
                  'ProjectionType': 'ALL' # Project all attributes into the index
                  # Other options: 'KEYS_ONLY', 'INCLUDE' (specific attributes)
               },
               'ProvisionedThroughput': {
                  'ReadCapacityUnits': 1,
                  'WriteCapacityUnits': 1,
               }
            }      
         ]
      )

      # table.add_global_secondary_index(
      #    index_name="category-index",
      #    partition_key=aws_dynamodb.Attribute(
      #          name="category", type=aws_dynamodb.AttributeType.STRING
      #    )
      # )

      for product in sample_products:
         products_db.upsert_product(product['id'], product)

