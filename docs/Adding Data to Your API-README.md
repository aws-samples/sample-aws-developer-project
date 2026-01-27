# Core API Stack - Adding Data to Your API

Learn persistent data storage by building a product catalog API using AWS Lambda, Amazon API Gateway, and DynamoDB. This stack builds upon the Initial API Stack by adding a NoSQL database for data persistence.

## What You Will Build

This stack creates a production-ready serverless API with:
- **REST API** with full CRUD operations (GET, POST, PUT, DELETE, OPTIONS)
- **Lambda functions** handling each API operation
- **DynamoDB table** for persistent data storage
- **Global Secondary Index** for efficient category-based queries
- **CORS support** for web application integration
- **Infrastructure as Code** using AWS CDK

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

This stack creates:
- **Lambda functions** - Pay per execution ([AWS Lambda Pricing](https://aws.amazon.com/lambda/pricing/))
- **API Gateway** - Pay per request ([API Gateway Pricing](https://aws.amazon.com/api-gateway/pricing/))
- **DynamoDB** - Pay per read/write capacity ([DynamoDB Pricing](https://aws.amazon.com/dynamodb/pricing/))

**Important:** Always destroy the stack when finished to avoid unnecessary charges.

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
cdk deploy CoreApiStack
```
**Note** If you are prompted with  `--require-approval is enabled and stack includes security-sensitive updates: 'Do you wish to deploy these changes(y/n)'` Select `y`
Save the `CoreApiStack.ProductsApiUrl` and `CoreApiStack.UIUrl` from the deployment output for testing.



## Project Structure

```
aws_developer_sample_project/
├── stacks/
│   └── core_api_stack.py         # CDK infrastructure definition
└── core_api/
    ├── get_product.py            # GET /products/{id}
    ├── query_products.py         # GET /products
    ├── insert_product.py         # POST /products
    ├── update_product.py         # PUT /products/{id}
    ├── delete_product.py         # DELETE /products/{id}
    ├── options.py                # CORS preflight handler
    ├── products_db.py            # DynamoDB operations
    └── response_utils.py         # Shared response formatting
```

## DynamoDB Table Design

**Table Name:** `core_api_products`

**Primary Key:**
- **Partition Key:** `id` (String) - Unique product identifier

**Global Secondary Index:**
- **Index Name:** `category-index`
- **Partition Key:** `category` (String) - Product category for filtering

**Sample Item:**
```json
{
  "id": "prod_001",
  "name": "Laptop",
  "price": 999.99,
  "category": "electronics",
  "description": "High-performance laptop",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

## API Endpoints

| Method | Endpoint | Description | Implementation Status |
|--------|----------|-------------|----------------------|
| GET | `/products` | List all products | ✅ Fully implemented |
| GET | `/products?category=electronics` | Filter by category | ✅ Fully implemented |
| GET | `/products/{id}` | Get product by ID | ✅ Fully implemented |
| POST | `/products` | Create new product | ✅ Fully implemented |
| PUT | `/products/{id}` | Update existing product | ✅ Fully implemented |
| DELETE | `/products/{id}` | Delete product | ✅ Fully implemented |
| OPTIONS | `/products` | CORS preflight for /products | ✅ Fully implemented |
| OPTIONS | `/products/{id}` | CORS preflight for /products/{id} | ✅ Fully implemented |
| GET | `/ui` | Web UI for testing API | ✅ Fully implemented |

## Testing Your API

You can test your application UI using the `CoreApiStack.UIUrl` or replace `<api-id>` and `<region>` with values in `CoreApiStack.ProductsApiUrl` from your deployment output.

Replace `<api-id>` and `<region>` with values from your deployment output.

### List All Products
```bash
curl https://<api-id>.execute-api.<region>.amazonaws.com/dev/products
```

### Filter Products by Category
```bash
curl "https://<api-id>.execute-api.<region>.amazonaws.com/dev/products?category=electronics"
```

### Create a New Product
```bash
curl -X POST https://<api-id>.execute-api.<region>.amazonaws.com/dev/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Wireless Mouse",
    "price": 29.99,
    "category": "electronics",
    "description": "Ergonomic wireless mouse"
  }'
```

### Get Single Product
```bash
curl https://<api-id>.execute-api.<region>.amazonaws.com/dev/products/<id>
```
**Sample output**: `{"category": "electronics", "description": "Ergonomic wireless mouse", "id": "1b2c3d4-5678-90ab-cdef-EXAMPLE11111", "price": 29.0, "title": ""}`

### Update a Product
```bash
curl -X PUT https://<api-id>.execute-api.<region>.amazonaws.com/dev/products/<id> \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Gaming Laptop",
    "price": 1299,
    "category": "electronics",
    "description": "High-performance gaming laptop"
  }'
```

### Delete a Product
```bash
curl -X DELETE https://<api-id>.execute-api.<region>.amazonaws.com/dev/products/<id>
```

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Partition Key** | Primary identifier for items |
| **Global Secondary Index** | Alternative query pattern |
| **Item** | Individual record in DynamoDB |
| **Scan vs Query** | Different data retrieval methods |
| **Capacity Units** | Read/write throughput measurement |

## DynamoDB Operations with AWS CLI

### View Table Information
```bash
# Describe the table
aws dynamodb describe-table --table-name core_api_products

# List all tables
aws dynamodb list-tables
```

### Query Data Directly
```bash
# Scan all items
aws dynamodb scan --table-name core_api_products

# Get specific item
aws dynamodb get-item --table-name core_api_products --key '{"id":{"S":"prod_001"}}'

# Query by category using GSI
aws dynamodb query --table-name core_api_products --index-name category-index --key-condition-expression "category = :cat" --expression-attribute-values '{":cat":{"S":"electronics"}}'
```


## Clean Up

**Important:** Always clean up to avoid ongoing charges
```bash
cdk destroy CoreApiStack
```

Confirm destruction when prompted. This will delete:
- DynamoDB table and all data
- Lambda functions
- API Gateway
- IAM roles and policies

## Troubleshooting

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| 502 Bad Gateway | Lambda function error | Check CloudWatch Logs for error details |
| 400 ValidationException | Invalid DynamoDB operation | Verify item structure and key attributes |
| 400 ProvisionedThroughputExceededException | Too many requests | Increase table capacity or implement retry logic |
| 404 Item not found | Product doesn't exist in DynamoDB | Verify product ID and table contents |
| CORS errors in browser | Missing CORS headers | Verify OPTIONS handler is working |
| "Unable to locate credentials" | AWS CLI not configured | Run `aws configure` or check credentials |

Learn containerized deployment with ECS

## Additional Resources

- [AWS Lambda Developer Guide](https://docs.aws.amazon.com/lambda/latest/dg/)
- [API Gateway Developer Guide](https://docs.aws.amazon.com/apigateway/latest/developerguide/)
- [DynamoDB Developer Guide](https://docs.aws.amazon.com/dynamodb/latest/developerguide/)
- [AWS CDK Python Reference](https://docs.aws.amazon.com/cdk/api/v2/python/)
- [DynamoDB Best Practices](https://docs.aws.amazon.com/dynamodb/latest/developerguide/best-practices.html)

