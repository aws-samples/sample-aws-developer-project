headers= {
   'Access-Control-Allow-Origin': '*', 
   'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS', 
   'Access-Control-Allow-Headers': 'Content-Type, Authorization',
   'Content-Type': 'text/html'
}

def create_success_response(data):
    """Create standardized success response for API Gateway"""
    return {
        'statusCode': 200,
        'headers': headers,
        'body': data
    }

def handler(event, context):
   with open('index.html', 'r', encoding='utf-8') as f:
        data = f.read()
   return create_success_response(data)
