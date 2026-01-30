# Initial API Stack - Building Your First Serverless API

Learn serverless fundamentals by building a product catalog API using AWS Lambda and Amazon API Gateway. This introductory stack uses in-memory data storage to focus on core serverless concepts without database complexity.

## What You Will Build

This stack creates a foundational serverless API with:
- **REST API** with GET, POST, PUT, and OPTIONS endpoints
- **Lambda functions** handling each API operation
- **CORS support** for web application integration
- **Infrastructure as Code** using AWS CDK
- **In-memory data store** for simplicity

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
- **Amazon API Gateway** - Pay per API request. For detailed pricing information, see  ([API Gateway Pricing](https://aws.amazon.com/api-gateway/pricing/))
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

### Step 4: Bootstrap CDK (First time only)
```bash
cdk bootstrap
```

### Step 5: Deploy the Stack

```bash
# Deploy the Initial API stack
cdk deploy InitialApiStack

# Expected output:
# InitialApiStack.ProductsApiUrl = https://abc123.execute-api.us-east-1.amazonaws.com/dev/products
# InitialApiStack.UIUrl = https://abc123.execute-api.us-east-1.amazonaws.com/dev/ui

```
**Note** If you are prompted with  `--require-approval is enabled and stack includes security-sensitive updates: 'Do you wish to deploy these changes(y/n)'` Select `y`
Save the `InitialApiStack.ProductsApiUrl` and `InitialApiStack.UIUrl` from the deployment output for testing.


## Project Structure

```
aws_developer_sample_project/
├── stacks/
│   └── initial_api_stack.py      # CDK infrastructure definition
└── initial_api/
    ├── get_product.py            # GET /products/{id}
    ├── query_products.py         # GET /products
    ├── insert_product.py         # POST /products (placeholder)
    ├── update_product.py         # PUT /products/{id} (placeholder)
    ├── delete_product.py         # DELETE /products/{id} (placeholder)
    ├── options.py                # CORS preflight handler
    ├── products_db.py            # In-memory data store
    └── response_utils.py         # Shared response formatting

```
## API Endpoints

| Method | Endpoint | Description | Implementation Status |
|--------|----------|-------------|----------------------|
| GET | `/products` | List all products | Fully implemented |
| GET | `/products/{id}` | Get product by ID | Fully implemented |
| POST | `/products` | Create new product | Placeholder only |
| PUT | `/products/{id}` | Update existing product | Placeholder only |
| OPTIONS | `/products` | CORS preflight for /products | Fully implemented |
| OPTIONS | `/products/{id}` | CORS preflight for /products/{id} | Fully implemented |
| GET | `/ui` | Web UI for testing API | Fully implemented |

## Testing Your API
You can test your application UI using the `InitialApiStack.UIUrl` or replace `<api-id>` and `<region>` with values `InitialApiStack.ProductsApiUrl` from your deployment output.


### List All Products
```bash
curl https://<api-id>.execute-api.<region>.amazonaws.com/dev/products
```

**Expected Response:** JSON array of sample products

### Get Single Product
```bash
curl https://<api-id>.execute-api.<region>.amazonaws.com/dev/products/prod_001
```

**Expected Response:** JSON object with product details

### Test Error Handling
```bash
curl https://<api-id>.execute-api.<region>.amazonaws.com/dev/products/invalid_id
```

**Expected Response:** 404 error with appropriate message

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Lambda Handler** | Entry point function receiving `event` and `context` |
| **Proxy Integration** | API Gateway forwards complete HTTP request to Lambda |
| **Event Object** | Contains path parameters, query strings, headers, body |
| **Response Format** | Must include `statusCode`, `headers`, and `body` |


## Clean Up

**Important:** Always clean up to avoid ongoing charges
```bash
cdk destroy InitialApiStack
```

Confirm destruction when prompted.

## Troubleshooting

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| 502 Bad Gateway | Lambda function error | Check CloudWatch Logs for error details |
| CORS errors in browser | Missing CORS headers | Verify OPTIONS handler is working |
| "Stack already exists" | Previous deployment exists | Run `cdk destroy` first, then redeploy |
| "Unable to locate credentials" | AWS CLI not configured | Run `aws configure` or check credentials |



## Additional Resources

- [AWS Lambda Developer Guide](https://docs.aws.amazon.com/lambda/latest/dg/)
- [API Gateway Developer Guide](https://docs.aws.amazon.com/apigateway/latest/developerguide/)
- [AWS CDK Python Reference](https://docs.aws.amazon.com/cdk/api/v2/python/)
- [Serverless Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)

