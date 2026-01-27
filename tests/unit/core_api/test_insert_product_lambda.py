import unittest
import os
import sys
import json
import moto
import boto3

folder_to_add = os.path.abspath('aws_developer_sample_project/core_api') 

@moto.mock_aws
class TestInsertProduct(unittest.TestCase):
   table_name = "Products"
   sample_products = [
      {
         'id': '1',
         'title': 'Product 1',
         'description': 'Product 1 description',
         'price': 10,
         'categories': ['category1', 'category2']
      },
      {
         'id': '2',
         'title': 'Product 2',
         'description': 'Product 2 description',
         'price': 20,
         'categories': ['category2', 'category3']
      }
   ]
      
   def setUp(self):
      sys.path.append(folder_to_add) 
      import aws_developer_sample_project.core_api.products_db as products_db
      self.products_db = products_db


      dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
      dynamodb.create_table(
         TableName = self.table_name,
         KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
         AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
         BillingMode='PAY_PER_REQUEST'
      )

      for product in self.sample_products:
         self.products_db.upsert_product(product['id'], product)

      import aws_developer_sample_project.core_api.insert_product as insert_product
      self.insert_product=insert_product

   def tearDown(self):
      sys.path.remove(folder_to_add)
      return super().tearDown()
   
   def test_insert_product(self):
      event={
         'body': json.dumps({
            'name': 'Product 1',
            'price': 100
         })
      }
      answer = self.insert_product.handler(event, None)
      self.assertEqual(answer['statusCode'], 200)

   def test_with_id(self):
      product_id = 'does not exist'
      event={
         'body': json.dumps({
            'id': product_id,
            'name': 'Product 1',
            'price': 100
         })
      }
      answer = self.insert_product.handler(event, None)
      self.assertEqual(answer.get('statusCode'), 400)
      self.assertEqual(answer['body'], 'Product id is not allowed')


@moto.mock_aws

class TestExceptions(unittest.TestCase):
   def setUp(self):
      sys.path.append(folder_to_add) 
   def tearDown(self):
      sys.path.remove(folder_to_add)
      return super().tearDown()

   def test_get_product_with_exception(self):
      import aws_developer_sample_project.core_api.get_product as the_lambda

      product_id = 'does not exist'
      event={
         'pathParameters': {
            'id': product_id
         }
      }
      answer = the_lambda.handler(event, None)
      self.assertEqual(answer['statusCode'], 500)

if __name__ == '__main__':
    unittest.main()
