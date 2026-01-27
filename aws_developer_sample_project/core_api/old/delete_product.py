from utils import create_success_response,create_error_response
import boto3
import json

def handler(event, context):
    path_parameters = event.get('pathParameters') or {}
    try:
         table=boto3.resource('dynamodb').Table('Products')
         product_id = path_parameters.get('id')
         if product_id:
            product=table.delete_item(Key={'id': product_id}).get('Item')
            if product:
               return create_success_response(200, product) 
            else:
                return create_error_response(404, 'Product not found')
         else: 
            create_error_response(400, 'Product id is required') 
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return create_error_response(500, f'Internal server error - {str(e)}')
