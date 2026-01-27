# AWS Developer Sample Project 
This project helps you learn AWS development by building a product catalog API using AWS CLI and CDK. You will deploy real AWS infrastructure and test working APIs.

## What You Will Build
This project demonstrates different AWS deployment patterns through five distinct stacks. Each stack implements the product catalog API using different technologies and architectural approaches, allowing you to compare and learn various AWS services.

**Stack Implementations:**
All CDK stack code is located in `aws_developer_sample_project/stacks/` folder.

- **Initial API** - Basic serverless API with Lambda and API Gateway using in-memory storage  
- **Core API** - Serverless API with DynamoDB for persistent data storage  
- **Full API** - Production-ready API with caching, S3, VPC, and authentication
- **Containers API** - Container-based deployment using ECS Fargate instead of Lambda  
- **CI/CD Stack** - Automated deployment pipeline with CodePipeline and CodeBuild  

For documentation on each feature, please see [the documentation](docs/)
## Prerequisites

**Required:**
- AWS Account (Free Tier recommended)
- Node.js 18+ and Python 3.12+
- Basic command line knowledge
- Git

**You Will Learn:**
- AWS CLI configuration and usage
- AWS CDK deployment
- AWS service interaction via CLI
- Infrastructure as Code concepts

## Setup Guide

### Step 1: Create AWS Account
1. Go to https://aws.amazon.com/free/
2. Sign up for Free Tier account
3. Complete verification (credit card required but will not be charged)

### Step 2: Install Required Tools

**Install AWS CLI v2:**
- **Windows**: Download from https://aws.amazon.com/cli/
- **macOS**: `brew install awscli` or download installer
- **Linux**: 
  ```bash
  curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
  unzip awscliv2.zip
  sudo ./aws/install
  ```

**Install Node.js:**
- Download LTS version from https://nodejs.org/
- Verify: `node --version` (should be v18+)

**Install Python:**
- Download Python 3.12+ from https://python.org/downloads/
- Verify: `python --version`

**Install Git:**
- Download from https://git-scm.com/downloads

### Step 3: Configure AWS CLI

**Create IAM User (Recommended):**
1. Go to **AWS Console > IAM > Users**
2. Choose **Create User**
3. Username: `cdk-developer`
4. Check **Programmatic access**
5. Attach policy: **AdministratorAccess** (for learning)
6. **Save the Access Key ID and Secret Access Key**

**Configure AWS CLI:**
```bash
aws configure
```
Enter:
- **AWS Access Key ID**: [Your access key]
- **AWS Secret Access Key**: [Your secret key]
- **Default region name**: `us-east-1` (recommended)
- **Default output format**: `json`

**Verify Configuration:**
```bash
# Test AWS CLI connection
aws sts get-caller-identity

# Should return your account info
{
    "UserId": "AIDACKCEVSQ6C2EXAMPLE",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/cdk-developer"
}
```

### Step 4: Clone and Setup Project

```bash
# Clone the repository
git clone https://github.com/aws-samples/sample-aws-developer-project
cd sample-aws-developer-project

# Create Python virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate.bat
# macOS/Linux:
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install AWS CDK globally
npm install -g aws-cdk

# Verify CDK installation
cdk --version
```

### Step 5: Bootstrap CDK

**First-time CDK setup in your AWS account:**
```bash
# Bootstrap CDK (creates S3 bucket and IAM roles for deployments)
cdk bootstrap

# Expected output:
# Environment aws://123456789012/us-east-1 bootstrapped
```

### Step 6: Explore Available Stacks

```bash
# List all available stacks
cdk ls

# Should show:
# InitialApiStack
# CoreApiStack
# FullApiStack
# ContainersStack
# CicdStack

# Preview what will be deployed (without deploying)
cdk synth InitialApiStack

# Compare deployed vs current state
cdk diff InitialApiStack
```


## Available Stacks

| Stack | Description | AWS Services | Use Case |
|-------|-------------|--------------|----------|
| **InitialApiStack** | Basic API with in-memory storage | Lambda, API Gateway | Learning serverless basics |
| **CoreApiStack** | API with persistent database | Lambda, API Gateway, DynamoDB | Learning data persistence |
| **FullApiStack** | Production-ready with caching | Lambda, API Gateway, DynamoDB, S3, ElastiCache, VPC | Advanced AWS features |
| **ContainersStack** | Container-based deployment | ECS, Fargate, ALB, DynamoDB | Learning containerization |
| **CicdStack** | CI/CD pipeline | CodePipeline, CodeBuild, CodeDeploy | Learning DevOps |

## Deployment Options
```bash
# Deploy the Initial API (simplest stack)
cdk deploy InitialApiStack

```bash
# Deploy specific stack
cdk deploy CoreApiStack

# Deploy multiple stacks
cdk deploy InitialApiStack CoreApiStack

# Deploy with approval for security changes
cdk deploy --require-approval never

# Deploy with custom parameters
cdk deploy FullApiStack -c create_cache=true -c authenticated=true

# Deploy all stacks
cdk deploy --all
```


## Clean Up Resources

**Important: Always clean up to avoid charges!**

```bash
# Destroy specific stack
cdk destroy InitialApiStack

# Destroy all stacks
cdk destroy --all

# Verify cleanup with AWS CLI
aws cloudformation list-stacks --stack-status-filter DELETE_COMPLETE

# Check for remaining Lambda functions
aws lambda list-functions --query 'Functions[?contains(FunctionName, `InitialApiStack`)]'
```

## Troubleshooting with AWS CLI

### Common Issues and Solutions

**"Unable to locate credentials"**
```bash
# Check current configuration
aws configure list

# Reconfigure if needed
aws configure

# Test connection
aws sts get-caller-identity
```

**"cdk command not found"**
```bash
# Check Node.js installation
node --version

# Reinstall CDK
npm install -g aws-cdk

# Verify installation
cdk --version
```

**"No module named 'aws_cdk'"**
```bash
# Ensure virtual environment is activated
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate.bat  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

**Lambda function errors**
```bash
# Get function name
aws lambda list-functions --query 'Functions[?contains(FunctionName, `InitialApiStack`)].FunctionName'

# View recent errors
aws logs filter-log-events --log-group-name "/aws/lambda/FUNCTION-NAME" --filter-pattern "ERROR"

# Get function configuration
aws lambda get-function-configuration --function-name FUNCTION-NAME
```


## Essential AWS CLI Commands Reference

```bash
# Identity and Access
aws sts get-caller-identity
aws iam list-users
aws iam get-user

# Lambda
aws lambda list-functions
aws lambda invoke --function-name NAME output.json
aws lambda get-function --function-name NAME

# API Gateway
aws apigateway get-rest-apis
aws apigateway test-invoke-method --rest-api-id ID --resource-id ID --http-method GET

# DynamoDB
aws dynamodb list-tables
aws dynamodb scan --table-name TABLE-NAME
aws dynamodb put-item --table-name TABLE-NAME --item file://item.json

# CloudFormation
aws cloudformation list-stacks
aws cloudformation describe-stacks --stack-name STACK-NAME
aws cloudformation get-template --stack-name STACK-NAME

# Logs
aws logs describe-log-groups
aws logs filter-log-events --log-group-name GROUP-NAME
```

## Additional Resources

- [AWS CLI Documentation](https://docs.aws.amazon.com/cli/)
- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [AWS Free Tier](https://aws.amazon.com/free/)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [Amazon API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [AWS CloudFormation Documentation](https://docs.aws.amazon.com/cloudformation/)

## License

This library is licensed under the MIT-0 License. See the LICENSE file.