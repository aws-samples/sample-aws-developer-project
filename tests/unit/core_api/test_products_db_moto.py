import unittest
import moto
import boto3


@moto.mock_aws
class TestProductsDB(unittest.TestCase):
   table_name = "Products"
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
      import aws_developer_sample_project.core_api.products_db as products_db
      self.products_db=products_db

      dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
      dynamodb.create_table(
         TableName = self.table_name,
         KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
         AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
         BillingMode='PAY_PER_REQUEST'
      )

      for product in self.sample_products:
         self.products_db.upsert_product(product['id'], product)

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
