import unittest
import os
import sys
import json
from unittest.mock import patch

folder_to_add = os.path.abspath('aws_developer_sample_project/initial_api') 
sys.path.append(folder_to_add) 

class TestGetProduct(unittest.TestCase):   
   def setUp(self):
      import aws_developer_sample_project.initial_api.get_product as get_product
      self.get_product=get_product

   def test_get__existing_product(self):
      product_id = 'prod_001' # we know it exists in our dummy data
      event={
         'pathParameters': {
            'id': product_id
         }
      }
      answer = self.get_product.handler(event, None)
      self.assertEqual(answer['statusCode'], 200)
      product=json.loads(answer['body'])
      self.assertEqual(product['id'], product_id)
      
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

class TestGetProductException(unittest.TestCase):
   import aws_developer_sample_project.initial_api.get_product as get_product

   @patch('products_db.get_product')
   def test_get_product_with_exception(self,mock_get_product):
      mock_get_product.side_effect = RuntimeError("Exception generated from test code")
      product_id = 'does not exist'
      event={
         'pathParameters': {
            'id': product_id
         }
      }
      answer = self.get_product.handler(event, None)
      self.assertEqual(answer['statusCode'], 500)

if __name__ == '__main__':
    unittest.main()
