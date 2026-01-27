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

sample_product = Product(
   title='Sample Product',
   description='This is a sample product',
   price=100.0,
   category='Sample Category'
)

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
      url = api_output['OutputValue']
      assert url.startswith("https")
      return url
   except Exception as e:
      print(f"Error retrieving API URL: {e}")
      return None


stack_name=os.getenv('STACK_NAME') or 'CoreApiStack'
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
      assert url.startswith('https')
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
      assert url.startswith('https')
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
      assert req.type=='https'
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

class TestProducts(unittest.TestCase):
   def test_add_product(self):
      p=add_product(sample_product)
      self.assertIsNotNone(p)
      self.assertEqual(p['title'], sample_product.title)
      self.assertEqual(p['description'], sample_product.description)
      self.assertEqual(p['price'], sample_product.price)
      self.assertEqual(p['category'], sample_product.category)
      pp=delete_product(p['id'])

   def test_update_product(self):
      product=copy.copy(sample_product)
      p=Product(**add_product(product))
      self.assertEqual(p.title, sample_product.title)
      self.assertEqual(p.description, sample_product.description)
      self.assertEqual(p.price, sample_product.price)
      self.assertEqual(p.category, sample_product.category)
      p.category='Updated Category'
      pp=Product(**update_product(p))
      self.assertIsNotNone(pp)
      self.assertEqual(p,pp)
      pp=delete_product(p.id)

   def test_everything_product(self):
      product=copy.copy(sample_product)
      p=Product(**add_product(product))
      self.assertEqual(p.title, sample_product.title)
      self.assertEqual(p.description, sample_product.description)
      self.assertEqual(p.price, sample_product.price)
      self.assertEqual(p.category, sample_product.category)
      p.category='Updated Category'
      pp=Product(**update_product(p))
      self.assertEqual(p,pp)
      pp=Product(**get_product(p.id))
      self.assertEqual(p,pp)
      delete_product(p.id)
      pp=get_product(p.id)
      self.assertIsNone(pp)

   def test_get_all_products(self):
      product=copy.copy(sample_product)
      product.category=str(uuid.uuid4())
      p=Product(**add_product(product))
      ps=get_all_products()
      print(f'{ps=}')
      pps=[Product(**product) for product in ps if product['id']==p.id]
      print(f'{pps=}')
      self.assertEqual(len(pps), 1)
      ps=get_products_by_category(product.category)
      for product in ps:
         self.assertEqual(product['category'], p.category)
      pps=[Product(**product) for product in ps if product['id']==p.id]
      self.assertEqual(len(pps), 1)
