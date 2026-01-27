from utils import create_success_response,create_error_response
import boto3
import json
from decimal import Decimal
import uuid

def handler(event, context):
   body = event.get('body') or ''
   try:
      item = json.loads(body)
      if 'id' in item:
         return create_error_response(400, 'Product id is not allowed')
      table=boto3.resource('dynamodb').Table('Products')
      id=str(uuid.uuid4())
      categories=item.get('categories') or []
      title=item.get('title') or ''
      description=item.get('description') or ''
      price=Decimal(item.get('price') or 0)

      update_expression = "SET categories = :categories, title = :title, description = :description, price = :price"
      expression_attribute_values = {
         ':categories': categories,
         ':title': title,
         ':description': description,
         ':price': price
      }
      if id:
         inserted=table.update_item(
            Key={'id': id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="ALL_NEW"
         )
         return create_success_response(200, inserted['Attributes'])
      else:
         return create_error_response(400, 'Product id is required')
   except Exception as e:
      print(f"Unexpected error: {str(e)}")
      return create_error_response(500, f'Internal server error - {str(e)}')
