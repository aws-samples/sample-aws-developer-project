import boto3
import json
import os
def update_product_images(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Products')
    
    product_id = event['pathParameters']['id']
    body = json.loads(event.get('body', '{}'))
    image_key = body['image_key'] 
    
    # Construct the public URL for the image
    bucket_name = os.getenv('S3_BUCKET', 'amzn-s3-demo-store-product-images-unique')
    image_url = f"https://{bucket_name}.s3.amazonaws.com/{image_key}"
    
    try:
        # Update the product with the new image URL
        response = table.update_item(
            Key={'id': product_id},
            UpdateExpression='SET image_urls = list_append(if_not_exists(image_urls, :empty_list), :new_image)',
            ExpressionAttributeValues={
                ':empty_list': [],
                ':new_image': [image_url]
            },
            ReturnValues='UPDATED_NEW'
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Product image updated successfully',
                'image_url': image_url
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Failed to update product',
                'details': str(e)
            })
        }
