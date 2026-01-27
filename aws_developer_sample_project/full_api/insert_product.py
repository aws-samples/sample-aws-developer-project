import json
from decimal import Decimal
import uuid
import products_db
from response_utils import create_success_response,create_error_response

def handler(event, context):
   body = event.get('body') or ''
   try:
      item = json.loads(body)
      if 'id' in item:
         return create_error_response(400, 'Product id is not allowed')
      inserted=products_db.insert_product(item)
      return create_success_response(200, inserted)
   except Exception as e:
      print(f"Unexpected error: {str(e)}")
      return create_error_response(500, f'Internal server error - {str(e)}')
