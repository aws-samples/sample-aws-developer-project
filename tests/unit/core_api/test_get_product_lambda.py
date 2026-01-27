import unittest
import boto3
import moto
import os
import json
from unittest.mock import patch
from .testing_utils import create_resources,sample_products,load_path

@moto.mock_aws
@load_path
class TestGetProducts(unittest.TestCase):    
   def setUp(self):
      import aws_developer_sample_project.core_api.products_db as products_db
      self.products_db = products_db
      
      import aws_developer_sample_project.core_api.get_product as get_product
      self.get_product=get_product
      create_resources(self.products_db)

   def test_get__existing_product(self):
      product_id = sample_products[0]['id']
      event={
         'pathParameters': {
            'id': product_id
         }
      }
      answer = self.get_product.handler(event, None)
      self.assertEqual(answer['statusCode'], 200)
      product=json.loads(answer['body'])
      self.assertEqual(product,sample_products[0])
      
   def test_get__non_existing_product(self):
      product_id = 'does not exist'
      event={
         'pathParameters': {
            'id': product_id
         }
      }
      answer = self.get_product.handler(event, None)
      self.assertEqual(answer['statusCode'], 404)
      
   def test_no_params(self):
      product_id = 'does not exist'
      event={
      }
      answer = self.get_product.handler(event, None)
      self.assertEqual(answer['statusCode'], 400)
      self.assertEqual(answer['body'], 'Product id is required')

@moto.mock_aws
@load_path
class TestExceptions(unittest.TestCase):
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
