# Full API Stack - Scaling with Data Storage

Learn advanced data storage patterns by building a production-ready product catalog API using AWS Lambda, Amazon API Gateway, DynamoDB, Amazon S3, and Amazon ElastiCache. This stack demonstrates how to handle diverse data types and optimize performance for real-world applications.

## What You Will Build

This stack creates a production-ready serverless API with:
- **REST API** with CRUD operations and file management
- **Lambda functions** handling API operations and event processing
- **DynamoDB table** for structured product data
- **Amazon S3 bucket** for product image storage with lifecycle policies
- **Amazon ElastiCache** for high-performance caching (optional)
- **Presigned URLs** for secure file uploads and downloads

## Prerequisites

**Required Tools:**
- AWS Account with appropriate permissions
- AWS CLI configured with credentials  
- Python 3.12+
- Node.js and npm
- AWS CDK CLI (`npm install -g aws-cdk`)
- Git

For detailed setup instructions, see [Project Setup](../README.md).


## Cost Information

**Important:** This application uses various AWS services and there are costs associated with these services after the Free Tier usage. You are responsible for any AWS costs incurred.

**Services Used:**
- **AWS Lambda** - Pay per execution and duration. For detailed pricing information, see ([AWS Lambda Pricing](https://aws.amazon.com/lambda/pricing/))
- **Amazon API Gateway** - Pay per API request. For detailed pricing information, see ([API Gateway Pricing](https://aws.amazon.com/api-gateway/pricing/))
- **Amazon DynamoDB** - Pay per read/write capacity. For detailed pricing information, see ([DynamoDB Pricing](https://aws.amazon.com/dynamodb/pricing/))
- **Amazon S3** - Pay for storage and requests. For detailed pricing information, see ([S3 Pricing](https://aws.amazon.com/s3/pricing/))
- **Amazon ElastiCache** - Pay for cache nodes. For detailed pricing information, see ([ElastiCache Pricing](https://aws.amazon.com/elasticache/pricing/))
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
# Deploy with basic features
cdk deploy FullApiStack

# Deploy with caching enabled
cdk deploy FullApiStack -c create_cache=true

```

Save the `FullApiStack.ProductsApiUrl` and `FullApiStack.UIUrl` from the deployment output for testing.


## Project Structure

```
aws_developer_sample_project/
├── stacks/
│   └── full_api_stack.py            # CDK infrastructure definition
└── full_api/
    ├── get_product.py               # GET /products/{id} with caching
    ├── query_products.py            # GET /products with caching
    ├── insert_product.py            # POST /products
    ├── update_product.py            # PUT /products/{id}
    ├── delete_product.py            # DELETE /products/{id}
    ├── generate_upload_url.py       # POST /products/{id}/images (upload)
    ├── generate_download_url.py     # GET /products/{id}/images (download)
    ├── process_uploaded_images.py   # S3 event trigger for image processing
    ├── update_product_images.py     # Update product with image URLs
    ├── products_db.py               # DynamoDB operations with caching
    └── response_utils.py            # Shared response formatting
```

## API Endpoints

| Method | Endpoint | Description | Implementation Status |
|--------|----------|-------------|----------------------|
| GET | `/products` | List all products with caching | Fully implemented |
| GET | `/products/{id}` | Get product by ID with caching | Fully implemented |
| POST | `/products` | Create new product | Fully implemented |
| PUT | `/products/{id}` | Update existing product | Fully implemented |
| DELETE | `/products/{id}` | Delete product | Fully implemented |
| POST | `/products/{id}/images` | Generate upload URL for images | Fully implemented |
| GET | `/products/{id}/images` | Generate download URL for images | Fully implemented |
| OPTIONS | `/products` | CORS preflight | Fully implemented |

## File Storage with Amazon S3

### Presigned URL Workflow

The stack implements secure file upload/download using presigned URLs:

**Upload Process:**
1. Client requests upload URL: `POST /products/{id}/images`
2. Lambda generates presigned URL for S3 PUT operation
3. Client uploads file directly to S3 using presigned URL
4. S3 triggers Lambda function to process uploaded image
5. Lambda updates product record with image URL

**Download Process:**
1. Client requests download URL: `GET /products/{id}/images`
2. Lambda generates presigned URL for S3 GET operation
3. Client downloads file directly from S3

### Prepare Test Files

Before testing file operations, you need an image file:

**Option 1: Create a test file**
```bash
# Unix/Linux/macOS
echo "fake image data" > product-image.jpg

# Windows
echo fake image data > product-image.jpg
```
**Option 2: Use existing image**
Use any .jpg file you have and rename it to product-image.jpg

### Testing File Operations

You can test your application UI using the `FullApiStack.UIUrl` or replace `<api-id>` and `<region>` with values in `FullApiStack.ProductsApiUrl` from your deployment output.

**Generate Upload URL:**
```bash
curl -X POST https://<api-id>.execute-api.<region>.amazonaws.com/dev/products/<id>/images?type=main
```

**Upload Image (using returned URL):**
```bash
curl -X PUT "<presigned-upload-url>" \
  -H "Content-Type: image/jpeg" \
  --data-binary @product-image.jpg
```

**Generate Download URL:**
```bash
curl https://<api-id>.execute-api.<region>.amazonaws.com/dev/products/<id>/images?type=main&size=large
```

## Caching with Amazon ElastiCache

### Cache-Aside Pattern

The stack implements the cache-aside pattern for optimal performance:

```python
def get_product(product_id):
   if not cluster_url:
      return get_product_from_dynamodb(product_id)
   cache_key = f"product:{product_id}"
   try:
      # Try cache first
      cached_product = cache_client.get(cache_key)
      if cached_product:
         print(f"Cache hit for product {product_id}")
         return json.loads(cached_product)
            
      # Cache miss - get from DynamoDB
      print(f"Cache miss for product {product_id}. Trying to get from dynamo")
      product = get_product_from_dynamodb(product_id)
      
      if product:
         product_str=json.dumps(product,default=decimal_serializer)
         # Store in cache with 1 hour TTL
         cache_client.setex(cache_key, 3600, product_str)
      
      return product
      
   except BaseException as e:
      print(f"Valkey error: {e}")
      # Fallback to database if cache fails
      return get_product_from_dynamodb(product_id)
```

### Cache Configuration

**TTL Strategies:**
- **Product details**: 1 hour (stable data)
- **Search results**: 30 minutes (balance freshness/performance)
- **Category lists**: 2 hours (rarely change)
- **Popular products**: 1 hour (trending data)

### Testing with Caching

**Enable caching during deployment:**
```bash
cdk deploy FullApiStack -c create_cache=true
```

**Monitor cache performance:**
- Check CloudWatch metrics for hit/miss ratios
- Monitor memory utilization
- Track response time improvements


## Key Concepts

| Concept | Description |
|---------|-------------|
| **Presigned URLs** | Temporary, secure access to S3 operations without AWS credentials |
| **Cache-Aside Pattern** | Check cache first, query database on miss, update cache |
| **TTL (Time To Live)** | Cache expiration strategy based on data change frequency |



## Clean Up

**Important:** Always clean up to avoid ongoing charges

```bash
# Destroy the stack
cdk destroy FullApiStack
```


## Troubleshooting

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| Presigned URL generation fails | Missing S3 permissions | Check Lambda execution role has S3 access |
| Image upload fails | Incorrect Content-Type | Ensure Content-Type matches presigned URL |
| MissingContentLength error | Missing Content-Length header | Add -H "Content-Length: $(wc -c < file)" to curl|
| Cache connection timeout | VPC configuration | Verify security groups allow port 6379 |
| S3 trigger not working | Event notification not configured | Check S3 bucket event configuration |
| High cache miss rate | TTL too short or cache not warmed | Increase TTL or implement cache warming |


## Additional Resources

- [AWS Lambda Developer Guide](https://docs.aws.amazon.com/lambda/latest/dg/)
- [Amazon S3 Developer Guide](https://docs.aws.amazon.com/s3/latest/userguide/)
- [Amazon ElastiCache User Guide](https://docs.aws.amazon.com/elasticache/latest/mem-ug/)
- [AWS CDK Python Reference](https://docs.aws.amazon.com/cdk/api/v2/python/)
- [Serverless Application Lens](https://docs.aws.amazon.com/wellarchitected/latest/serverless-applications-lens/)
