# Containers API Stack - Container Deployment

Learn container deployment concepts by implementing containerized applications using Amazon ECS, AWS Fargate, and Amazon ECR. This stack demonstrates when containers provide advantages over serverless functions and how to deploy scalable container services without managing underlying infrastructure.

## What You Will Build

This stack creates a containerized version of your product catalog API with:
- **Docker containerization** of your Python Flask application
- **Amazon ECR** for secure container image storage and management
- **Amazon ECS with AWS Fargate** for serverless container orchestration
- **Application Load Balancer** for traffic distribution and high availability
- **DynamoDB integration** for persistent data storage


## Prerequisites

**Required Tools:**
- AWS Account with appropriate permissions
- AWS CLI configured with credentials
- Docker or Finch for building and testing containers locally
- Python 3.12+
- Node.js and npm
- AWS CDK CLI
- Git

For detailed setup instructions, see [Project Setup](../README.md).

## Cost Information

**Important:** This application uses various AWS services and there are costs associated with these services after the Free Tier usage. You are responsible for any AWS costs incurred.

**Services Used:**
- **AWS Fargate** - Pay per vCPU and memory used. For detailed pricing information, see ([Fargate Pricing](https://aws.amazon.com/fargate/pricing/))
- **Application Load Balancer** - Pay per hour and per LCU. For detailed pricing information, see ([ALB Pricing](https://aws.amazon.com/elasticloadbalancing/pricing/))
- **Amazon ECR** - Pay for storage and data transfer. For detailed pricing information, see ([ECR Pricing](https://aws.amazon.com/ecr/pricing/))
- **Amazon DynamoDB** - Pay per read/write capacity. For detailed pricing information, see ([DynamoDB Pricing](https://aws.amazon.com/dynamodb/pricing/))
- **Amazon S3** - Pay for storage and requests. For detailed pricing information, see ([S3 Pricing](https://aws.amazon.com/s3/pricing/))
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
# Deploy the containerized API
cdk deploy ContainersStack
```

Save the `ContainersStack.ProductsApiUrl` and `ContainersStack.UIUrl` from the deployment output for testing.

## Project Structure

```
aws_developer_sample_project/
├── stacks/
│   └── containers_stack.py         # CDK infrastructure definition
└── containers/
    ├── templates/
    │   └── index.html               # Web UI template
    ├── app.py                       # Flask web application
    ├── products_db.py               # DynamoDB operations
    ├── utils.py                     # Utility functions
    ├── requirements.txt             # Python dependencies
    ├── Dockerfile                   # Container image definition
    └── comments.txt                 # Implementation notes
```


## API Endpoints

| Method | Endpoint | Description | Implementation Status |
|--------|----------|-------------|----------------------|
| GET | `/` | Web UI homepage | Fully implemented |
| GET | `/products` | List all products (with category filtering) | Fully implemented |
| GET | `/products/{id}` | Get product by ID | Fully implemented |
| POST | `/products` | Create new product | Fully implemented |
| DELETE | `/products/{id}` | Delete product | Fully implemented |
| OPTIONS | `/products` | CORS preflight | Fully implemented |
| OPTIONS | `/products/{id}` | CORS preflight | Fully implemented |


### Testing Your Containerized API

You can test your application UI using the `ContainersStack.UIUrl` or replace `<load-balancer-url>` with the `ContainersStack.ProductsApiUrl` from your deployment output.

**Test Web Interface:**
```bash
curl http://<load-balancer-url>/
```

**Test Product Listing:**
```bash
curl http://<load-balancer-url>/products
```

**Create New Product:**
```bash
curl -X POST http://<load-balancer-url>/products \
  -H "Content-Type: application/json" \
  -d '{"name": "Container Product", "price": 29.99, "category": "electronics"}'
```

**Filter Products by Category:**
```bash
curl http://<load-balancer-url>/products?category=electronics
```


### Container Deployment Workflow

1. **Build Container Image** - Package application with dependencies
2. **Store in Amazon ECR** - Secure, managed container registry
3. **Define ECS Task** - Specify container configuration and resources
4. **Create ECS Service** - Manage desired container instances
5. **Configure Load Balancing** - Distribute traffic across containers

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Container Image** | Packaged application with all dependencies and runtime |
| **Task Definition** | Blueprint specifying container configuration and resources |
| **ECS Service** | Manages desired number of running task instances |
| **Fargate** | Serverless compute engine eliminating EC2 management |
| **Application Load Balancer** | Distributes traffic and performs health checks |
| **ECR Repository** | Secure storage for container images with lifecycle policies |

## Implementation Status

### Currently Implemented
- Docker containerization of Flask application
- ECS Fargate service with auto-scaling
- Application Load Balancer integration
- DynamoDB data persistence
- CloudWatch logging and monitoring
- ARM64 architecture for cost optimization


## Clean Up

**Important:** Always clean up to avoid ongoing charges

```bash
# Destroy the stack
cdk destroy ContainersStack
```

## Troubleshooting

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| Container fails to start | Image build errors or missing dependencies | Check CloudWatch logs for container startup errors |
| Load balancer health checks fail | Application not listening on correct port | Verify container exposes port 5000 and app binds to 0.0.0.0 |
| High container costs | Over-provisioned resources | Monitor CPU/memory usage and right-size task definition |
| Slow container startup | Large image size | Optimize Dockerfile with multi-stage builds and minimal base images |
| Database connection errors | IAM permissions or network configuration | Verify task role has DynamoDB permissions |

## Additional Resources

- [Amazon ECS Developer Guide](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/)
- [AWS Fargate User Guide](https://docs.aws.amazon.com/AmazonECS/latest/userguide/what-is-fargate.html)
- [Amazon ECR User Guide](https://docs.aws.amazon.com/AmazonECR/latest/userguide/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [AWS CDK Python Reference](https://docs.aws.amazon.com/cdk/api/v2/python/)
- [Container Security Best Practices](https://aws.amazon.com/blogs/containers/security-best-practices-for-amazon-ecs/)