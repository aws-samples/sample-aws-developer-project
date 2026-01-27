# Full API Stack - Real-time Data Streaming

Learn real-time data streaming concepts by implementing streaming data ingestion and processing using AWS Lambda and Amazon Kinesis Data Streams. This stack extends your existing API to capture customer activity streams and deliver transformed data to analytics systems for immediate insights.

## What You Will Build

This stack extends the existing FullApiStack with basic streaming capabilities:
- **Amazon Kinesis Data Streams** for product price updates 
- **AWS Lambda function** for processing price change events 
- **Stream-to-database integration** for updating product prices 

## Prerequisites

**Required Tools:**
- AWS Account with appropriate permissions
- AWS CLI configured with credentials
- Python 3.12+
- Node.js and npm
- AWS CDK CLI 
- Git
For detailed setup instructions, see [Project Setup](../README.md).

## Cost Information

**Important:** This application uses various AWS services and there are costs associated with these services after the Free Tier usage. You are responsible for any AWS costs incurred.

**Services Used:**
- **AWS Lambda** - Pay per execution and duration. For detailed pricing information, see ([AWS Lambda Pricing](https://aws.amazon.com/lambda/pricing/))
- **Amazon API Gateway** - Pay per API request. For detailed pricing information, see ([API Gateway Pricing](https://aws.amazon.com/api-gateway/pricing/))
- **Amazon Kinesis Data Streams** - Pay per shard hour. For detailed pricing information, see ([Kinesis Pricing](https://aws.amazon.com/kinesis/data-streams/pricing/))
- **Amazon Data Firehose** - Pay per GB ingested. For detailed pricing information, see ([Data Firehose Pricing](https://aws.amazon.com/kinesis/data-firehose/pricing/))
- **Amazon S3** - Pay for storage and requests. For detailed pricing information, see ([S3 Pricing](https://aws.amazon.com/s3/pricing/))
- **Amazon DynamoDB** - Pay per read/write capacity. For detailed pricing information, see ([DynamoDB Pricing](https://aws.amazon.com/dynamodb/pricing/))
- **AWS CloudFormation** - No additional charges for stack operations.

**Note**: Always destroy stacks when finished to avoid ongoing charges

## Quick Start

### Step 1: Get the Project
```bash
git clone https://github.com/aws-samples/sample-aws-developer-project
cd sample-aws-developer-project
```

### Step 2: Set Up Environment
**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Bootstrap CDK (First Time Only)
```bash
cdk bootstrap
```

### Step 5: Deploy the Stack
```bash

# Deploy with Kinesis stream enabled
cdk deploy FullApiStack -c create_stream=true

```

**Save the API URL from the deployment output** - you will need it for testing.

## Project Structure

```
aws_developer_sample_project/
├── stacks/
│   └── full_api_stack.py            # CDK infrastructure definition
└── full_api/
    ├── get_product.py               # GET /products/{id}
    ├── query_products.py            # GET /products
    ├── insert_product.py            # POST /products
    ├── update_product.py            # PUT /products/{id}
    ├── delete_product.py            # DELETE /products/{id}
    ├── generate_upload_url.py       # POST /products/{id}/images (upload)
    ├── generate_download_url.py     # GET /products/{id}/images (download)
    ├── process_uploaded_images.py   # S3 event trigger for image processing
    ├── update_product_images.py     # Update product with image URLs
    ├── process_stream_prices.py     # Kinesis stream processing (implemented)
    ├── products_db.py               # DynamoDB operations
    ├── response_utils.py            # Shared response formatting
    └── utils.py                     # Utility functions
```



## API Endpoints

| Method | Endpoint | Description | Implementation Status |
|--------|----------|-------------|----------------------|
| GET | `/products` | List all products | Fully implemented |
| GET | `/products/{id}` | Get product by ID | Fully implemented |
| POST | `/products` | Create new product | Fully implemented |
| PUT | `/products/{id}` | Update existing product | Fully implemented |
| DELETE | `/products/{id}` | Delete product | Fully implemented |
| POST | `/products/{id}/images` | Generate upload URL for images | Fully implemented |
| GET | `/products/{id}/images` | Generate download URL for images | Fully implemented |
| OPTIONS | `/products` | CORS preflight | Fully implemented |

## Streaming Implementation

### Kinesis Data Streams Processing

The stack includes Kinesis stream processing for product price updates:

**Current Implementation:**
- **ProductPricesStream** - Kinesis Data Stream for price updates
- **process_stream_prices.py** - Lambda function processing price events
- **Automatic scaling** - Stream scales based on data volume

### Testing Stream Processing

**1. List All Streams:**
```bash
aws kinesis list-streams
```

**2. Check Stream Status:**
```bash
aws kinesis describe-stream --stream-name ProductPricesStream
aws kinesis describe-stream --stream-name ProductPricesStream --region <region>
```

**Send Test Price Update:**
```bash
aws kinesis put-record \
  --stream-name ProductPricesStream \
  --partition-key "prod_001" \
  --data '{"product_id": "prod_001", "price": 29.99}' \
  --region <region>
```


## Key Concepts

| Concept | Description |
|---------|-------------|
| **Streaming Data** | Continuous flow of data processed in real-time |


## Implementation Status

### Currently Implemented
- Kinesis Data Streams with price processing
- Lambda stream processing functions
- Basic stream-to-database integration


## Clean Up

**Important:** Always clean up to avoid ongoing charges

```bash
# Destroy the stack
cdk destroy FullApiStack
```

## Troubleshooting

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| Stream processing errors | Lambda function timeout | Increase timeout or optimize processing logic |
| High stream costs | Too many shards provisioned | Monitor usage and adjust shard count |
| Data delivery delays | Buffer settings too large | Reduce buffer size or time thresholds |
| Transformation failures | Invalid data format | Add data validation and error handling |
| Missing stream data | Partition key issues | Ensure proper partition key distribution |

## Additional Resources

- [AWS Lambda Developer Guide](https://docs.aws.amazon.com/lambda/latest/dg/)
- [Amazon Kinesis Data Streams Developer Guide](https://docs.aws.amazon.com/kinesis/latest/dev/)
- [Amazon Data Firehose Developer Guide](https://docs.aws.amazon.com/firehose/latest/dev/)
- [AWS CDK Python Reference](https://docs.aws.amazon.com/cdk/api/v2/python/)
- [Real-time Analytics Best Practices](https://docs.aws.amazon.com/kinesis/latest/dev/kinesis-record-processor-scaling.html)