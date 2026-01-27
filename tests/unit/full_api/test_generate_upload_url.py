import unittest
import boto3
import moto
import os
import sys
import json
from unittest.mock import patch

folder_to_add = os.path.abspath('aws_developer_sample_project/initial_api') 
sys.path.append(folder_to_add) 

@moto.mock_aws
class TestGenerateUploadUrl(unittest.TestCase):
   
   def setUp(self):
      import aws_developer_sample_project.module6.generate_upload_url as the_lambda
      self.the_lambda=the_lambda

      s3 = boto3.resource("s3", region_name="us-east-1")
      s3.create_bucket(Bucket="mybucket")
      os.environ['BUCKET_NAME'] = 'mybucket'

   def test_get_url(self):
      event={
         'pathParameters': {
            'id': 1
         },
         'queryStringParameters': {
            'type': 'main'
         }
      }
      answer = self.the_lambda.handler(event, None)
      print(f'{answer=}')
      self.assertEqual(answer['statusCode'], 200)
      body = json.loads(answer['body'])
      self.assertEqual(body['url'].split('?')[0], 'https://mybucket.s3.amazonaws.com/products/1/main.jpg') 
      self.assertTrue('expires_in' in body)

      
   def test_no_params(self):
      event={
      }
      answer = self.the_lambda.handler(event, None)
      self.assertEqual(answer['statusCode'], 400)
      self.assertEqual(answer['body'], 'Product id is required')

   def test_no_bucket_name(self):
      os.environ.pop('BUCKET_NAME', None)
      event={
         'pathParameters': {
            'id': 1
         },
         'queryStringParameters': {
            'type': 'main'
         }
      }
      answer = self.the_lambda.handler(event, None)
      self.assertEqual(answer['statusCode'], 500)

class TestExceptions(unittest.TestCase):

   @patch('boto3.client')
   def test_get_product_with_exception(self,mock_resource):
      product_id = 1
      event={
         'pathParameters': {
            'id': product_id
         },
         'queryStringParameters': {
            'type': 'main'
         }
      }

      mock_resource.return_value = None
      os.environ['BUCKET_NAME'] = 'mybucket'
      import aws_developer_sample_project.module6.generate_upload_url as the_lambda

      answer = the_lambda.handler(event, None)
      self.assertEqual(answer['statusCode'], 500)

if __name__ == '__main__':
    unittest.main()
