# CI/CD Pipeline API Stack - CI/CD Automation

Learn CI/CD pipeline automation concepts by implementing continuous integration and continuous delivery using AWS CodePipeline, AWS CodeBuild, and AWS CloudFormation. This stack transforms manual deployments into automated workflows that run when you commit code changes, with integrated testing and infrastructure deployment via CloudFormation changesets.

## What You Will Build

This stack creates a complete CI/CD pipeline for your product catalog API:
- **AWS CodeCommit** repository for source code management
- **AWS CodePipeline** for orchestrating multi-stage deployment workflows
- **AWS CodeBuild** for automated building, testing, and artifact creation
- **AWS CloudFormation** integration for infrastructure deployment
- **Manual approval gates** for production deployment control
- **Automated changeset creation** with preview before deployment

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
- **AWS CodePipeline** - Pay per active pipeline. For detailed pricing information, see ([CodePipeline Pricing](https://aws.amazon.com/codepipeline/pricing/))
- **AWS CodeBuild** - Pay per build minute. For detailed pricing information, see ([CodeBuild Pricing](https://aws.amazon.com/codebuild/pricing/))
- **AWS CodeCommit** - Pay per active user. For detailed pricing information, see ([CodeCommit Pricing](https://aws.amazon.com/codecommit/pricing/))
- **AWS Lambda** - Pay per execution and duration. For detailed pricing information, see ([AWS Lambda Pricing](https://aws.amazon.com/lambda/pricing/))
- **Amazon API Gateway** - Pay per API request. For detailed pricing information, see ([API Gateway Pricing](https://aws.amazon.com/api-gateway/pricing/))
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

### Step 5: Deploy the CI/CD Pipeline
```bash
# Deploy the CI/CD infrastructure
cdk deploy CICDStack
```

Save the Repository URL from the deployment output to push code changes.

## Project Structure

```
aws_developer_sample_project/
├── stacks/
│   ├── cicd_stack.py                # CI/CD pipeline infrastructure
│   └── full_api_stack.py            # Application infrastructure
├── buildspec.yaml                   # CodeBuild build specification
└── full_api/
    ├── get_product.py               # GET /products/{id}
    ├── query_products.py            # GET /products
    ├── insert_product.py            # POST /products
    ├── update_product.py            # PUT /products/{id}
    ├── delete_product.py            # DELETE /products/{id}
    ├── generate_upload_url.py       # POST /products/{id}/images
    ├── generate_download_url.py     # GET /products/{id}/images
    ├── process_uploaded_images.py   # S3 event trigger for image processing
    ├── products_db.py               # DynamoDB operations
    └── utils.py                     # Utility functions
```

## CI/CD Pipeline Architecture

### Pipeline Stages

**Current Implementation:**
1. **Source Stage** - Monitors CodeCommit repository for changes (implemented)
2. **Build Stage** - Runs CodeBuild project with buildspec.yaml (implemented)
3. **Deploy Stage** - Creates CloudFormation changeset and deploys after approval (implemented)


## Current Implementation Details

### CodeCommit Repository
- **Repository Name**: ProductsCatalog
- **Purpose**: Source code storage and version control
- **Integration**: Triggers pipeline on code commits to main branch

### CodeBuild Project
- **Build Specification**: Uses `buildspec.yaml` for build instructions
- **Permissions**: Can assume CDK roles for deployment
- **Artifacts**: Creates deployment packages for CloudFormation

### Pipeline Configuration
- **Pipeline Name**: ProductsCatalogPipeline
- **Restart on Update**: Automatically restarts when pipeline definition changes
- **Manual Approval**: Required before production deployment
- **CloudFormation Integration**: Executes changesets for infrastructure updates



## Testing Your CI/CD Pipeline

### Step 1: Clone the Repository
```bash
# Get repository URL from CICDStack deployment output
git clone <repository-https-url>
cd ProductsCatalog
```

**Note:** For HTTPS cloning, you will need Git credentials from AWS Console → IAM → Your User → Security credentials → "HTTPS Git credentials for AWS CodeCommit" → Generate credentials. Use these Git credentials (not your AWS console login) when prompted.

### Step 2: Copy Project Files to Repository
**Windows:**
```bash
# Copy all project files from sample-aws-developer-project
copy "..\sample-aws-developer-project\*.*" .
xcopy "..\sample-aws-developer-project\aws_developer_sample_project" aws_developer_sample_project /E /I /Y
xcopy "..\sample-aws-developer-project\tests" tests /E /I /Y
```

**macOS/Linux:**
```bash
# Copy all project files from sample-aws-developer-project
cp ../sample-aws-developer-project/*.* .
cp -r ../sample-aws-developer-project/aws_developer_sample_project .
cp -r ../sample-aws-developer-project/tests .
```

### Step 3: Commit and Push Files
```bash
# Add all files to git
git add .

# Commit the files
git commit -m "Initial commit - add complete project files"

# Push to trigger the pipeline
git push origin main
```

### Step 4: Monitor Pipeline Execution
1. Open AWS Console → CodePipeline
2. Find "ProductsCatalogPipeline"
3. Watch stages execute: Source → Build → Deploy
4. Approve manual approval when prompted
5. Verify deployment completes successfully




## Key Concepts 

| Concept | Description |
|---------|-------------|
| **CI/CD Pipeline** | Automated workflow from code commit to production deployment |
| **Source Stage** | Monitors repository and triggers pipeline on code changes |
| **Build Stage** | Compiles code, runs tests, creates deployment artifacts |
| **Deploy Stage** | Deploys artifacts to target environment |
| **Build Specification** | YAML file defining build commands and phases |
| **Pipeline Artifacts** | Files passed between pipeline stages |
| **Manual Approval** | Human gate before production deployment |

## Implementation Status

### Currently Implemented
- CodeCommit repository for source control
- CodePipeline with source, build, and deploy stages
- CodeBuild project with IAM permissions for CDK deployment
- Manual approval gate before production deployment
- CloudFormation changeset creation and execution
- Integration with existing FullApiStack

## Clean Up

**Important:** Always clean up to avoid ongoing charges

```bash
# Destroy the application stack first (if deployed by pipeline)
cdk destroy FullApiStack

# Then destroy the CI/CD stack
cdk destroy CICDStack

# Note: This will also delete the CodeCommit repository and all code
```  

## Troubleshooting

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| Pipeline fails at source stage | Repository empty or no commits | Push code to CodeCommit repository |
| Build stage fails | Missing buildspec.yaml or syntax errors | Verify buildspec.yaml exists and is valid YAML |
| Permission denied during build | Missing IAM permissions | Check CodeBuild role has CDK deployment permissions |
| CloudFormation deployment fails | Invalid CDK template or resource conflicts | Review CloudFormation error messages and fix CDK code |
| Manual approval stuck | No notification configured | Check AWS Console for pending approvals |
| Pipeline not triggering | Branch configuration mismatch | Verify pipeline monitors correct branch (main) |

## Additional Resources

- [AWS CodePipeline User Guide](https://docs.aws.amazon.com/codepipeline/latest/userguide/)
- [AWS CodeBuild User Guide](https://docs.aws.amazon.com/codebuild/latest/userguide/)
- [AWS CodeCommit User Guide](https://docs.aws.amazon.com/codecommit/latest/userguide/)
- [AWS CodeDeploy User Guide](https://docs.aws.amazon.com/codedeploy/latest/userguide/)
- [CDK Pipelines Guide](https://docs.aws.amazon.com/cdk/v2/guide/cdk_pipeline.html)
- [AWS CDK Python Reference](https://docs.aws.amazon.com/cdk/api/v2/python/)