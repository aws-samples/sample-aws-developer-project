import unittest
import os
import sys
import json
from unittest.mock import patch
folder_to_add = os.path.abspath('aws_developer_sample_project/initial_api') 
sys.path.append(folder_to_add) 

class TestInsertProduct(unittest.TestCase):
      
   def setUp(self):
      import aws_developer_sample_project.initial_api.insert_product as insert_product
      self.insert_product=insert_product

   def test_insert_product(self):
      product_id = 'prod_001' 
      event={
         'body': json.dumps({
            'name': 'Product 1',
            'price': 100
         })
      }
      answer = self.insert_product.handler(event, None)
      self.assertEqual(answer['statusCode'], 500)

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


if __name__ == '__main__':
    unittest.main()
