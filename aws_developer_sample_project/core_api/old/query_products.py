from utils import create_success_response,create_error_response
import boto3
import json

def handler(event, context):
   path_parameters = event.get('pathParameters') or {}
   try:
      table=boto3.resource('dynamodb').Table('Products')
      query_parameters=event.get('queryStringParameters') or {}
      category=query_parameters.get('category')
      if category:
         products=table.scan(FilterExpression=boto3.dynamodb.conditions.Attr('categories').contains(category)).get('Items')
         return create_success_response(200, products)
      else: 
         create_error_response(400, 'Category is required') 
   except Exception as e:
      print(f"Unexpected error: {str(e)}")
      return create_error_response(500, f'Internal server error - {str(e)}')
