import unittest
import os
import sys
import json
from unittest.mock import patch
folder_to_add = os.path.abspath('aws_developer_sample_project/initial_api') 
sys.path.append(folder_to_add) 

class TestUpdateProduct(unittest.TestCase):
      
   def setUp(self):
      import aws_developer_sample_project.initial_api.update_product as update_product
      self.update_product=update_product

   def test_without_id(self):
      event={
         'body': json.dumps({
            'name': 'Product 1',
            'price': 100
         })
      }
      answer = self.update_product.handler(event, None)
      self.assertEqual(answer['statusCode'], 400)

   def test_with_id(self):
      product_id = 'prod1'
      event={
         'pathParameters': {
            'id': product_id
         },
         'body': json.dumps({
            'name': 'Product 1',
            'price': 100
         })
      }
      answer = self.update_product.handler(event, None)
      self.assertEqual(answer.get('statusCode'), 500)


if __name__ == '__main__':
    unittest.main()
