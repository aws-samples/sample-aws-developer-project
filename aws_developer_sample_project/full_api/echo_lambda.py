from response_utils import create_success_response,create_error_response

def handler(event, context):
   print(event)
   return create_success_response(200, event) 
