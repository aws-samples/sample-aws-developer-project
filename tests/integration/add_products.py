import os
import sys
import boto3
from dataclasses import dataclass,asdict
import urllib.request
import urllib.parse
import json
import traceback
import unittest
import copy
import uuid

@dataclass 
class Product:
   title: str
   description: str
   price: int
   category: str
   id: str = None

sample_products = [
   Product(
      title='Sample Product 1',
      description='This is the first sample product',
      price=110.0,
      category='Odd Category'
   ),
   Product(
      title='Sample Product 2',
      description='This is the second sample product',
      price=120.0,
      category='Even Category'
   ),
   Product(
      title='Sample Product 3',
      description='This is the third sample product',
      price=130.0,
      category='Odd Category'
   ),
   Product(
      title='Sample Product 4',
      description='This is the fourth sample product',
      price=140.0,
      category='Even Category'
   ),
   Product(
      title='Sample Product 5',
      description='This is the fifth sample product',
      price=150.0,
      category='Odd Category'
   ),
]



headers = {"Content-Type": "application/json"}

def get_boto_client(service):
   if os.environ.get('ENDPOINT_URL'):
      return boto3.client(service,endpoint_url=os.environ.get('ENDPOINT_URL'))
   else:    
      return boto3.client(service)
   
def get_base_url(stack_name):
   try:
      response = get_boto_client('cloudformation').describe_stacks(StackName=stack_name)
      outputs = response['Stacks'][0]['Outputs']
      api_output = next(output for output in outputs if output['OutputKey'] == 'ProductsApiUrl')
      print(f"{api_output=}")
      return api_output['OutputValue']
   except Exception as e:
      print(f"Error retrieving API URL: {e}")
      return None

stack_name=os.getenv('STACK_NAME') or 'core_apiStack'
base_url=get_base_url(stack_name)

def safely_open(request):
   if request.type=="https":
      return urllib.request.urlopen(request)

def add_product(p):
   url=base_url+'/products'
   method='POST'
   data=asdict(p)
   if 'id' in data:
      del data['id']
   try:
      encoded_data = json.dumps(data).encode('utf-8')
      req = urllib.request.Request(url, data=encoded_data,method=method, headers=headers)
      with safely_open(req) as response:
         response_body = response.read().decode('utf-8')
         return json.loads(response_body)
   except urllib.error.URLError as e:
      print(f"Error: {e.reason}")
      traceback.print_exc()
      return None

def update_product(p):
   url=base_url+f'/products/{p.id}'
   method='PUT'
   data=asdict(p)
   if 'id' in data:
      del data['id']
   try:
      encoded_data = json.dumps(data).encode('utf-8')
      req = urllib.request.Request(url, data=encoded_data, method=method, headers=headers)
      with safely_open(req) as response:
         response_body = response.read().decode('utf-8')
         return json.loads(response_body)
   except urllib.error.URLError as e:
      print(f"Error: {e.reason}")
      traceback.print_exc()
      return None

def delete_product(id):
   url=base_url+f'/products/{id}'
   method='DELETE'
   try:
      req = urllib.request.Request(url, method=method, headers=headers)
      with safely_open(req) as response:
         response_body = response.read().decode('utf-8')
         return json.loads(response_body)
   except urllib.error.URLError as e:
      print(f"Error: {e.reason}")
      traceback.print_exc()
      return None

def get_product(id):
   url=base_url+f'/products/{id}'
   method='GET'
   try:
      req = urllib.request.Request(url,method='GET')
      with safely_open(req) as response:
         response_body = response.read().decode('utf-8')
         return json.loads(response_body)
   except urllib.error.URLError as e:
      if e.code==404:
         return None
      print(f"Error: {e.reason}")
      traceback.print_exc()
      return None

def get_all_products():
   url=base_url+f'/products'
   method='GET'
   try:
      req = urllib.request.Request(url,method='GET')
      with safely_open(req) as response:
         response_body = response.read().decode('utf-8')
         return json.loads(response_body)
   except urllib.error.URLError as e:
      if e.code==404:
         return None
      print(f"Error: {e.reason}")
      traceback.print_exc()
      return None

def get_products_by_category(cat):
   url=base_url+f'/products?category={cat}'
   method='GET'
   try:
      req = urllib.request.Request(url,method='GET')
      with safely_open(req) as response:
         response_body = response.read().decode('utf-8')
         return json.loads(response_body)
   except urllib.error.URLError as e:
      if e.code==404:
         return None
      print(f"Error: {e.reason}")
      traceback.print_exc()
      return None

for p in sample_products:
   print(f"Adding product {p.title}")
   add_product(p)
