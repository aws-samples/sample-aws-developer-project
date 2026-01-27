from response_utils import create_success_response,create_error_response
from products_db import get_products_by_category, get_all_products

def handler(event, context):
   path_parameters = event.get('pathParameters') or {}
   try:
      query_parameters=event.get('queryStringParameters') or {}
      category=query_parameters.get('category')
      if category:
         products=get_products_by_category(category)
      else: 
         products=get_all_products()
      return create_success_response(200, products)
   except Exception as e:
      print(f"Unexpected error: {str(e)}")
      return create_error_response(500, f'Internal server error - {str(e)}')
