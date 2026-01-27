import unittest
import unittest.mock
import boto3.dynamodb.conditions

def apply_update_expression(update_expression, expression_attribute_values,item):
   update_expression=update_expression.strip()
   if (update_expression.startswith('SET')):
      update_expression=update_expression[4:].strip()
      exprs=update_expression.split(',')
      for expr in exprs:
         key, value=expr.split('=')
         item[key.strip()]=expression_attribute_values.get(value.strip())
   return item

class Expando(object):
   def __init__(self, **kwargs):
      self.__dict__.update(kwargs)
      
class TestUpdateExpression(unittest.TestCase):
   def test_update_expression(self):
      update_expression = """
         SET categories = :categories,
         title = :title,
         description = :description,
         price = :price
      """
      expression_attribute_values = {
         ':categories': ['category1', 'category2'],
         ':title': 'Product 1',
         ':description': 'Product 1 description',
         ':price': 10
      }
      item=apply_update_expression(update_expression, expression_attribute_values,{})
      self.assertEqual(item['categories'], ['category1', 'category2'])
      self.assertEqual(item['title'], 'Product 1')
      self.assertEqual(item['description'], 'Product 1 description')
      self.assertEqual(item['price'], 10)

class MyDynamoTableMock(unittest.mock.MagicMock):
   id_field_name='id'

   data={}
   def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
   def get_item(self, Key):
      id=Key[self.id_field_name]
      return {'Item': self.data.get(id)}
   def delete_item(self, Key):
      id=Key[self.id_field_name]
      return self.data.pop(id)
   def update_item(self, Key, UpdateExpression, ExpressionAttributeValues, ReturnValues):
      id=Key[self.id_field_name]
      stored=self.data.get(id,{})
      item=apply_update_expression(UpdateExpression, ExpressionAttributeValues,stored)
      item[self.id_field_name]=id
      self.data[id]=item
      return {'Attributes': item}
   def scan(self, FilterExpression=None):
      if FilterExpression is None:
         return {'Items': list(self.data.values())}
      else:
         # not fully implemented, just what we use
         category=FilterExpression._values[1]
         return {'Items': [item for item in self.data.values() if category in item['categories']]}   

table_mock=MyDynamoTableMock()

class MyDynamoResourceMock(unittest.mock.MagicMock):
   def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
   def Table(self, table_name):
      return table_mock

class MyBotoMock(unittest.mock.MagicMock):
   def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
   def resource(self,module):
      if module == 'dynamodb':
         return table_mock
      return unittest.mock.MagicMock()
   dynamodb=Expando(conditions=Expando(
      Attr=lambda x: Expando(
         contains=lambda x: x
      )
   ))


class TestProductsDB(unittest.TestCase):
   sample_products = [
      {
         'id': '1',
         'title': 'Product 1',
         'description': 'Product 1 description',
         'price': 10,
         'categories': ['category1', 'category2']
      },
      {
         'id': '2',
         'title': 'Product 2',
         'description': 'Product 2 description',
         'price': 20,
         'categories': ['category2', 'category3']
      }
   ]
   def setUp(self):
      self.patcher = unittest.mock.patch('boto3.resource')
      self.mock_resource = self.patcher.start()
      self.mock_resource.return_value = table_mock
      import aws_developer_sample_project.module10.products_db as products_db
      self.products_db=products_db
      for product in self.sample_products:
         products_db.upsert_product(product['id'], product)

   def test_get_product(self):
      product_id = '1'
      product = self.products_db.get_product(product_id)
      self.assertEqual(product['id'], product_id)

   def test_delete_product(self):
      product_id = '2'
      product = self.products_db.get_product(product_id)
      self.assertEqual(product['id'], product_id) # it exists
      product=self.products_db.delete_product(product_id)
      self.assertEqual(product,None) # got deleted
      product = self.products_db.get_product(product_id)
      self.assertEqual(product,None) # doesn't exist anymore

   def test_add_product(self):
      product = {
         'title': 'Product 4',
         'description': 'Product 4 description',
         'price': 40,
         'categories': ['category4', 'category5']
      }
      inserted = self.products_db.insert_product(product)
      product_id=inserted['id']
      inserted = self.products_db.get_product(product_id)
      self.assertEqual(product['title'], inserted['title'])
      self.assertEqual(product['description'], inserted['description'])
      self.assertEqual(product['price'], inserted['price'])
      self.assertEqual(product['categories'], inserted['categories'])

   def test_query_products_by_category(self):
      products = self.products_db.get_products_by_category('category2')
      self.assertEqual(len(products), 2)
      for p in products:
         self.assertTrue(p in self.sample_products)

if __name__ == '__main__':
    unittest.main()
