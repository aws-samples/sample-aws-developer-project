import boto3
import os
import PIL
from io import BytesIO
from dataclasses import dataclass

@dataclass
class ImageSize:
   name: str
   width: int
   height: int

sizes=[
   ImageSize('small', 192, 108),
   ImageSize('medium', 1280, 720),
   ImageSize('large', 1920, 1080)
]

@dataclass
class ImageAttributes:
   product_id: str
   type: str

   @staticmethod
   def from_key(key):
      # f"{image_folder}/{product_id}/{image_type}.jpg"
      components=key.split('/')
      file_name=components[-1]
      product_id=file_name.split('.')[-2]
      type=file_name.split('.')[-1]
      return ImageAttributes(product_id=product_id, type=type)   


def update_products_table(product_id, image_type, sizes):
   table=boto3.resource('dynamodb').Table("Products")
   item_key = {
      'id': product_id
   }
   # in case the field is not set, initialize
   table.update_item(
      Key=item_key,
      UpdateExpression="SET images=if_not_exists(images, :empty_map)",
      ExpressionAttributeValues={
         ':empty_map':{},
      },
      ReturnValues="UPDATED_NEW"
   )
   # update the image types
   response = table.update_item(
      Key=item_key,
      UpdateExpression="SET images.#type=:sizes",
      ExpressionAttributeValues={
         ':sizes':[s.name for s in sizes],
      },
      ExpressionAttributeNames={
         '#type': image_type
      },
      ReturnValues="UPDATED_NEW"
   )

images_folder=os.environ.get('IMAGES_FOLDER') or 'product_images'
def process_image(bucket_name,key, product_id, type, output_folder,sizes):
   s3_client = boto3.client('s3')
   # Download the image from S3
   response = s3_client.get_object(Bucket=bucket_name, Key=key)
   image_content = response['Body'].read()
   for size in sizes:
      with PIL.Image.open(BytesIO(image_content)) as img:
         # Resize the image
         resized_img = img.resize((size.width, size.height))
         # Save the resized image back to S3
         output_key = f"{output_folder}/{product_id}/{type}/{size.name}.jpg"
         s3_client.put_object(Bucket=bucket_name, Key=output_key, Body=resized_img.tobytes())
      
def handler(event, context):
   # Process each S3 event record
   for record in event['Records']:
      bucket_name = record['s3']['bucket']['name']
      object_key = record['s3']['object']['key']
      attrs=ImageAttributes.from_key(object_key)
      
      try:
         process_image(bucket_name, object_key, images_folder, attrs.product_id, attrs.type,sizes)         
         
         print(f"Processed image metadata for product {attrs.product_id}")
            
      except Exception as e:
            print(f"Error processing {object_key}: {e}")
    
