import json
from decimal import Decimal
from flask import make_response

access_control_headers= {
    'Access-Control-Allow-Origin': '*', 
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS', 
    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
}
headers={**access_control_headers, 'Content-Type': 'application/json'}

def create_options_response():
    response=make_response('', 200, access_control_headers)

def create_success_response(status_code, data):
    return make_response(json.dumps(data, default=decimal_serializer), status_code, headers)

def create_error_response(status_code, message):
    return make_response(json.dumps({
        'error': message,
        'statusCode': status_code
        }), status_code, headers)

def decimal_serializer(obj):
    """Handle Decimal objects in JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")