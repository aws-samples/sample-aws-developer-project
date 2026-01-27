import uuid
from decimal import Decimal

PRODUCT_CATALOG = {
    "prod_001": {
        "id": "prod_001",
        "title": "Wireless Headphones",
        "price": 99.99,
        "category": "Electronics",
        "in_stock": True
    },
    "prod_002": {
        "id": "prod_002",
        "title": "Coffee Maker",
        "price": 149.99,
        "category": "Appliances",
        "in_stock": True
    }
}

def get_product(product_id):
   return PRODUCT_CATALOG.get(product_id)

def insert_product(item):
   raise NotImplementedError("This function is not implemented yet....")    

def delete_product(product_id):
   raise NotImplementedError("This function is not implemented yet.")    

def update_product(product_id, item):
   raise NotImplementedError("This function is not implemented yet.")    

def get_all_products():
   return list(PRODUCT_CATALOG.values())

def get_products_by_category(category):
   return [p for p in PRODUCT_CATALOG.values() if category== p.get('category')]