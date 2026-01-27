import boto3
import json
import os
from utils import create_success_response,create_error_response

def handler(event, context):
   try:
      s3_client = boto3.client('s3')
      bucket_name = os.environ.get('BUCKET_NAME')
      image_folder = os.environ.get('IMAGE_FOLDER') or 'product_images'
      if not bucket_name:
         return create_error_response(500, "Misconfiguration. BUCKET_NAME is required")
      
      product_id = event.get('pathParameters',{}).get('id')
      image_type = event.get('queryStringParameters',{}).get('type', 'main')
      image_size = event.get('queryStringParameters',{}).get('size', 'large')
      if not product_id:
         return create_error_response(400, "Product id is required")
      object_key = f"{image_folder}/{product_id}/{image_type}/{image_size}.jpg"
      # Generate presigned URL for GET operation
      download_url = s3_client.generate_presigned_url(
         'get_object',
         Params={
               'Bucket': bucket_name,
               'Key': object_key
         },
         ExpiresIn=3600  # URL expires in 1 hour
      )
      return create_success_response(200, {'download_url': download_url, 'expires_in':3600})      
      
   except Exception as e:
      print(f"Eror - {e}")
      return create_error_response(500, f'Failed to generate download URL - {e}',)