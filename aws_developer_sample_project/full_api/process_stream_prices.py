import base64
import json
from products_db import update_price

def handler(event, context):

    for record in event['Records']:
        try:
            print(f"Processing Kinesis Event - EventID: {record['eventID']}")
            record_data = base64.b64decode(record['kinesis']['data']).decode('utf-8')
            record_data=json.loads(record_data)
            print(f"Record Data: {record_data}")
            update_price(record_data['product_id'],record_data['price'])
        except Exception as e:
            print(f"An error occurred {e}")
            raise e
    print(f"Successfully processed {len(event['Records'])} records.")
