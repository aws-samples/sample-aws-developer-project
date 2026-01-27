from response_utils import create_success_response,create_error_response
import products_db

def handler(event, context):
    try:
         path_parameters = event.get('pathParameters') or {}
         product_id = path_parameters.get('id')
         if product_id:
            product=products_db.get_product(product_id)
            if product:
               return create_success_response(200, product) 
            else:
                return create_error_response(404, 'Product not found')
         else: 
            return create_error_response(400, 'Product id is required') 
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return create_error_response(500, f'Internal server error - {str(e)}')
