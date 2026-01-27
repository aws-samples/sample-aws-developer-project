import unittest
import os
import sys
import json
from unittest.mock import patch
folder_to_add = os.path.abspath('aws_developer_sample_project/initial_api') 
sys.path.append(folder_to_add) 

class TestDeleteProduct(unittest.TestCase):
      
   def setUp(self):
      import aws_developer_sample_project.initial_api.delete_product as delete_product
      self.delete_product=delete_product

   def test_delete_product(self):
      product_id = 'prod_001' 
      event={
         'pathParameters': {
            'id': product_id
         }
      }
      answer = self.delete_product.handler(event, None)
      self.assertEqual(answer['statusCode'], 500)

      
   def test_no_params(self):
      import aws_developer_sample_project.initial_api.delete_product as delete_product

      product_id = 'does not exist'
      event={
      }
      answer = self.delete_product.handler(event, None)
      self.assertEqual(answer.get('statusCode'), 400)
      self.assertEqual(answer['body'], 'Product id is required')

class TestDeleteProductException(unittest.TestCase):
   import aws_developer_sample_project.initial_api.delete_product as delete_product
   @patch('products_db.delete_product')
   def test_get_product_with_exception(self,mock_get_product):
      mock_get_product.side_effect = RuntimeError("Exception generated from test code")
      product_id = 'does not exist'
      event={
         'pathParameters': {
            'id': product_id
         }
      }
      answer = self.delete_product.handler(event, None)
      self.assertEqual(answer['statusCode'], 500)


if __name__ == '__main__':
    unittest.main()
