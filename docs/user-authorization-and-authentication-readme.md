# Full API Stack - User Authentication & Authorization

Learn authentication and authorization concepts by implementing secure user management using Amazon Cognito, IAM roles, and API Gateway authorizers. This stack transforms your functional API into a secure platform that protects customer data and controls access to sensitive operations.

## What You Will Build

This stack extends your existing API with authentication and authorization features:
- **Amazon Cognito User Pools** for customer authentication and user management 
- **JWT Token Authentication** with automatic validation via API Gateway authorizers 
- **IAM Execution Roles** for secure service-to-service authorization 
- **Protected Endpoints** for create, update, and delete operations 
- **Presigned URLs** for secure, time-limited S3 access without exposing credentials 

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
- **Amazon Cognito** - Pay per monthly active user. For detailed pricing information, see ([Cognito Pricing](https://aws.amazon.com/cognito/pricing/))
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

### Step 5: Deploy with Authentication
```bash
# Deploy with Cognito authentication enabled
cdk deploy FullApiStack -c authenticated=true -c cognito_domain=your-unique-domain
```

Save the Cognito URLs from the deployment ouput for user registration and login.

## Project Structure

```
aws_developer_sample_project/
├── stacks/
│   └── full_api_stack.py            # CDK infrastructure with Cognito integration
└── full_api/
    ├── get_product.py               # GET /products/{id}
    ├── query_products.py            # GET /products
    ├── insert_product.py            # POST /products (protected)
    ├── update_product.py            # PUT /products/{id} (protected)
    ├── delete_product.py            # DELETE /products/{id} (protected)
    ├── generate_upload_url.py       # POST /products/{id}/images (protected)
    ├── generate_download_url.py     # GET /products/{id}/images
    ├── process_uploaded_images.py   # S3 event trigger for image processing
    ├── update_product_images.py     # Update product with image URLs
    ├── products_db.py               # DynamoDB operations
    ├── response_utils.py            # Shared response formatting
    └── utils.py                     # Utility functions
```


## API Endpoints

| Method | Endpoint | Description | Authentication Required |
|--------|----------|-------------|------------------------|
| GET | `/products` | List all products | No |
| GET | `/products/{id}` | Get product by ID | No |
| POST | `/products` | Create new product | **Yes - JWT Token** |
| PUT | `/products/{id}` | Update existing product | **Yes - JWT Token** |
| DELETE | `/products/{id}` | Delete product | **Yes - JWT Token** |
| POST | `/products/{id}/images` | Generate upload URL for images | **Yes - JWT Token** |
| GET | `/products/{id}/images` | Generate download URL for images | No |
| GET | `/ui` | Web UI homepage | No |
| OPTIONS | `/*` | CORS preflight | No |

## Authentication Implementation

### User Registration & Login

**Registration Process:**
1. Customer provides email, password, and name
2. Cognito creates account with UNCONFIRMED status
3. Verification email sent automatically
4. Customer confirms email to activate account

**Login Process:**
1. Customer provides email and password
2. Cognito validates credentials
3. Returns three JWT tokens: ID token, Access token, Refresh token
4. Application stores tokens for API requests


### Testing Authentication

**Access Cognito Login URL:**
```
https://your-domain.auth.region.amazoncognito.com/login?client_id=CLIENT_ID&response_type=token&redirect_uri=REDIRECT_URL
```

**Test Protected Endpoint:**
```bash
# This will fail without authentication
curl -X POST https://api-url/products \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Product", "price": 29.99}'

# This will succeed with valid JWT token
curl -X POST https://api-url/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"name": "Authenticated Product", "price": 29.99}'
```




## Key Concepts

| Concept | Description |
|---------|-------------|
| **JWT Token** | JSON Web Token containing user claims and permissions |
| **Cognito User Pool** | Managed user directory with authentication workflows |
| **API Gateway Authorizer** | Validates JWT tokens before requests reach Lambda |
| **IAM Execution Role** | Provides Lambda functions secure access to AWS services |
| **Presigned URL** | Time-limited URL for direct S3 access without credentials |


## Implementation Status

### Currently Implemented
- Cognito User Pool with email verification
- App Client with OAuth 2.0 configuration
- API Gateway Cognito Authorizer
- Protected endpoints for create, update, delete operations
- IAM execution roles with least privilege permissions
- S3 presigned URL generation for image uploads


## Clean Up

**Important:** Always clean up to avoid ongoing charges

```bash
# Destroy the stack
cdk destroy FullApiStack
```

## Troubleshooting

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| 401 Unauthorized on protected endpoints | Missing or invalid JWT token | Include valid Access Token in Authorization header |
| User registration fails | Weak password or invalid email | Check password meets policy requirements |
| Email verification not received | Email in spam or incorrect address | Check spam folder, verify email address |
| AccessDeniedException in Lambda | Missing IAM permissions | Check execution role has required service permissions |
| CORS errors in browser | Missing Authorization header in CORS config | Verify API Gateway CORS includes Authorization header |
| Token expired errors | Access token expired (1 hour default) | Use refresh token to get new access token |

## Additional Resources

- [Amazon Cognito Developer Guide](https://docs.aws.amazon.com/cognito/latest/developerguide/)
- [AWS IAM User Guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/)
- [API Gateway Authorizers](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-authorizers.html)
- [JWT Token Best Practices](https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/)
- [AWS Security Best Practices](https://docs.aws.amazon.com/security/latest/userguide/best-practices.html)
- [AWS CDK Python Reference](https://docs.aws.amazon.com/cdk/api/v2/python/)