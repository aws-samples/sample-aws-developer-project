from response_utils import create_success_response,create_error_response
import json
from decimal import Decimal
from products_db import update_product

def handler(event, context):
   try:
      body = event.get('body') or ''
      id=event.get('pathParameters',{}).get('id')
      item = json.loads(body)

      if id:
         updated=update_product(id,item)
         return create_success_response(200, updated)
      else:
         return create_error_response(400, 'Product id is required')
   except Exception as e:
      print(f"Unexpected error: {str(e)}")
      return create_error_response(500, f'Internal server error - {str(e)}')
