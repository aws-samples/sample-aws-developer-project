# Full Api Stack - Advanced Lambda Patterns for Optimization and Resilience

Learn Lambda layers and configuration management by implementing shared dependencies and environment-specific settings. Package common libraries like Redis and Pillow into reusable layers, reducing deployment sizes and improving function performance across your serverless application.

## What You Will Build

This module extends your existing API with Lambda layer optimization:
- **Redis Layer** for caching functionality with shared Redis client libraries
- **Pillow Layer** for image processing with shared PIL dependencies  
- **Layer Build Scripts** for automated layer packaging and deployment


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
- **Amazon S3** - Pay for storage and requests. For detailed pricing information, see ([S3 Pricing](https://aws.amazon.com/s3/pricing/))
- **Amazon DynamoDB** - Pay per read/write capacity. For detailed pricing information, see ([DynamoDB Pricing](https://aws.amazon.com/dynamodb/pricing/))
- **Amazon ElastiCache** - Pay per cache node hour. For detailed pricing information, see ([ElastiCache Pricing](https://aws.amazon.com/elasticache/pricing/))
- **AWS CloudFormation** - No additional charges for stack operations.

**Note**: Always destroy stacks when finished to avoid ongoing charges

## Install Finch

- **Finch** (container runtime for layer building)
```bash
# macOS
brew install finch

# Linux
curl -L https://github.com/runfinch/finch/releases/latest/download/finch-$(uname -m).tar.gz | tar -xz
sudo mv finch /usr/local/bin/

# Windows
winget install Amazon.Finch
```

**Alternative:** Replace `finch run` with `docker run` in build scripts if you prefer Docker.

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

### Step 5: Build Lambda Layers
```bash
cd aws_developer_sample_project/layers

# Build Redis layer for caching functionality
./build-redis-layer.sh

# Build Pillow layer for image processing
./build-pil-layer.sh
```

### Step 6: Deploy the Stack
```bash
# Deploy with caching enabled to use Redis layer
cdk deploy FullApiStack -c create_cache=true

# Deploy with basic features (layers still included)
cdk deploy FullApiStack
```

Save the `FullApiStack.ProductsApiUrl` and `FullApiStack.UIUrl` from the deployment output for testing.


## Project Structure

```
aws_developer_sample_project/
├── layers/
│   ├── build-layer.sh               # Generic layer build script
│   ├── build-redis-layer.sh         # Redis layer build script
│   ├── build-pil-layer.sh           # Pillow layer build script
│   ├── redis-layer-requirements.txt # Redis dependencies
│   ├── pil-layer-requirements.txt   # Pillow dependencies
│   ├── redis-layer-python.zip       # Built Redis layer (generated)
│   └── pil-layer-python.zip         # Built Pillow layer (generated)
├── stacks/
│   └── full_api_stack.py            # CDK infrastructure with layer definitions
└── full_api/
    ├── get_product.py               # Uses Redis layer for caching
    ├── query_products.py            # Uses Redis layer for caching
    ├── insert_product.py            # Uses Redis layer for caching
    ├── update_product.py            # Uses Redis layer for caching
    ├── delete_product.py            # Uses Redis layer for caching
    ├── process_uploaded_images.py   # Uses Pillow layer for image processing
    ├── products_db.py               # DynamoDB operations
    ├── response_utils.py            # Shared response formatting
    └── utils.py                     # Utility functions
```



**Layer Structure:**
```
redis-layer-python.zip
└── python/
    ├── redis/
    │   ├── __init__.py
    │   ├── client.py
    │   └── [other redis modules]
    └── [dependency modules]
```


## Testing Layer Implementation

### Layer Functionality Testing

**Test Redis Layer:**
```bash
# Deploy with caching enabled
cdk deploy FullApiStack -c create_cache=true

# Test cached product retrieval
curl https://your-api-url/products/test-product-1

# Verify cache hit on second request (faster response)
curl https://your-api-url/products/test-product-1
```

**Test Pillow Layer:**
```bash
# Upload an image to trigger processing
curl -X POST https://your-api-url/products/test-product/images \
  -H "Content-Type: application/json" \
  -d '{"action": "upload"}'

# Check CloudWatch logs for image processing
aws logs filter-log-events \
  --log-group-name "/aws/lambda/FullApiStack-ProcessImages" \
  --start-time $(date -d '5 minutes ago' +%s)000
```

## Layer Management Best Practices

### Version Management

**Layer Versioning Strategy:**
```bash
# Create new layer version
aws lambda publish-layer-version \
    --layer-name redis-utilities \
    --description "Redis client v2.0 - Added connection pooling" \
    --zip-file fileb://redis-layer-python.zip \
    --compatible-runtimes python3.12
```

**Function Updates:**
```bash
# Update function to use new layer version
aws lambda update-function-configuration \
    --function-name FullApiStack-QueryProducts \
    --layers arn:aws:lambda:region:account:layer:redis-utilities:2
```



## Key Concepts

| Concept | Description |
|---------|-------------|
| **Lambda Layer** | Packaged code and dependencies shared across multiple functions |
| **Layer Version** | Immutable snapshot of layer code with unique ARN |
| **Compatible Architecture** | CPU architecture (ARM64/x86_64) that layer supports |
| **Layer Extraction** | Process of extracting layer contents to /opt in execution environment |
| **Environment Variables** | Runtime configuration values passed to Lambda functions |
| **Dependency Management** | Strategy for packaging and sharing external libraries |
| **Cold Start Optimization** | Techniques to minimize function initialization time |
| **Deployment Package** | ZIP file containing function code and dependencies |

## Implementation Status

### Currently Implemented
- Redis layer with automated build scripts
- Pillow layer for image processing
- CDK layer version management with RETAIN policy
- Environment variable configuration for all functions
- Layer attachment to appropriate functions
- ARM64 architecture optimization


## Clean Up

**Important:** Always clean up to avoid ongoing charges

```bash
# Destroy the stack
cdk destroy FullApiStack
```


**Note:** Lambda layers with RETAIN policy may persist after stack deletion and incur minimal storage costs.

## Troubleshooting

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| Layer build fails | Missing Docker/Finch | Install Docker Desktop or Finch container runtime |
| Import errors in functions | Layer not attached or wrong architecture | Verify layer ARN and compatible architecture |
| Large cold start times | Too many layers or large layer sizes | Optimize layer contents, use fewer layers |
| Layer version not found | Layer deleted or wrong region | Check layer ARN and region in function configuration |
| Permission denied on layer | Missing IAM permissions | Ensure Lambda execution role can access layers |
| Build script permission denied | Script not executable | Run `chmod +x build-*.sh` on build scripts |

## Additional Resources

- [AWS Lambda Layers Developer Guide](https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html)
- [Lambda Layer Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [AWS CDK Lambda Layers](https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_lambda/LayerVersion.html)
- [Lambda Environment Variables](https://docs.aws.amazon.com/lambda/latest/dg/configuration-envvars.html)
- [Container Images for Layer Building](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-using-build.html)
- [AWS CDK Python Reference](https://docs.aws.amazon.com/cdk/api/v2/python/)