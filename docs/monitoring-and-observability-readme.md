# Monitoring and Observability Guide

Learn how to monitor and observe your AWS Developer Sample Project deployments using built-in CloudWatch integration, logging, and metrics across all five stack architectures.

## What You Can Monitor

This project includes comprehensive monitoring capabilities across serverless, containerized, and CI/CD architectures:
- **Lambda Performance** - Duration, errors, concurrency limits
- **API Gateway** - Request metrics, caching, latency
- **Database Operations** - DynamoDB read/write capacity
- **Container Health** - ECS service metrics, load balancer status
- **Pipeline Execution** - CI/CD build and deployment tracking
- **Security Events** - Authentication, encryption key usage

## Prerequisites

**Required Tools:**
- AWS CLI configured with appropriate permissions
- Deployed stack (any of the 5 available stacks)
- Basic familiarity with CloudWatch console

**Optional Tools:**
- Apache Bench for load testing
- jq for JSON parsing

## Quick Start

### Step 1: Deploy a Stack
```bash
# Choose any stack to monitor
cdk deploy InitialApiStack
# OR
cdk deploy CoreApiStack
# OR
cdk deploy FullApiStack
```

### Step 2: Get Your API URL
```bash
# From deployment output, save the API URL
export API_URL="https://your-api-gateway-url"
```

### Step 3: Generate Some Traffic
```bash
# Create test data to monitor
curl -X POST $API_URL/products -H "Content-Type: application/json" -d '{"name":"Test Product","price":29.99}'
curl $API_URL/products
```

### Step 4: View Metrics
```bash
# Check Lambda performance
aws logs tail /aws/lambda/YourFunctionName --follow
```

## Stack Monitoring Capabilities

### InitialApiStack - Basic Serverless Monitoring

**What is Monitored:**
- Lambda function performance and concurrency
- API Gateway caching and request metrics
- Basic CloudWatch integration

**Test Concurrency Limits:**
```bash
# Test reserved concurrency (5 per function)
for i in {1..10}; do curl -X POST $API_URL/products & done
```

**Test API Caching:**
```bash
# First request creates cache entry
curl $API_URL/products/test-product-1

# Second request should be faster (cache hit)
time curl $API_URL/products/test-product-1
```

**View Performance Metrics:**
```bash
# Lambda duration metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=InitialApiStack-GetProduct \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 300 --statistics Average

# API Gateway cache metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name CacheHitCount \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 300 --statistics Sum
```

### CoreApiStack - Enhanced Security Monitoring

**What is Monitored:**
- Encrypted CloudWatch logs with KMS
- API Gateway access logging
- Structured function naming and log groups
- KMS key usage and rotation

**View Encrypted Logs:**
```bash
# List all CoreApi log groups
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/CoreApi"

# View specific function logs
aws logs filter-log-events --log-group-name "/aws/lambda/CoreApi_GetProduct"

# Search for errors across all functions
aws logs filter-log-events \
  --log-group-name "/aws/lambda/CoreApi_GetProduct" \
  --filter-pattern "ERROR"
```

**Monitor API Access:**
```bash
# View detailed API Gateway logs
aws logs filter-log-events --log-group-name "CoreApiStack-ApiGWLogGroup"

# Filter by status codes
aws logs filter-log-events \
  --log-group-name "CoreApiStack-ApiGWLogGroup" \
  --filter-pattern "[timestamp, request_id, ip, user, timestamp2, method, resource, protocol, status=4*, size, referer, agent]"
```

**Check KMS Usage:**
```bash
# Monitor encryption key usage
aws cloudwatch get-metric-statistics \
  --namespace AWS/KMS \
  --metric-name NumberOfRequestsSucceeded \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 300 --statistics Sum
```

### FullApiStack - Enterprise Multi-Service Monitoring

**What is Monitored:**
- Lambda functions with Redis caching
- S3 event-driven image processing
- Kinesis stream processing
- Cognito authentication events
- ElastiCache performance metrics
- VPC and security group activity

**Deploy with Advanced Features:**
```bash
# Enable caching
cdk deploy FullApiStack -c create_cache=true

# Enable streaming
cdk deploy FullApiStack -c create_stream=true

# Enable authentication
cdk deploy FullApiStack -c authenticated=true
```

**Test Caching Performance:**
```bash
# Monitor ElastiCache metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ElastiCache \
  --metric-name CacheHits \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 300 --statistics Sum

# Test cache performance
curl $API_URL/products/cached-product  # Cache miss
curl $API_URL/products/cached-product  # Cache hit
```

**Test S3 Event Processing:**
```bash
# Upload image to trigger processing
echo "test image data" > test-image.png
aws s3 cp test-image.png s3://your-bucket-name/incoming_product_images/

# Monitor image processing function
aws logs tail /aws/lambda/FullApiStack-ProcessImages --follow
```

**Monitor Stream Processing:**
```bash
# Check Kinesis stream metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Kinesis \
  --metric-name IncomingRecords \
  --dimensions Name=StreamName,Value=ProductPricesStream \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 300 --statistics Sum
```

**Test Authentication Monitoring:**
```bash
# Test authentication failure
curl -X POST $API_URL/products \
  -H "Authorization: Bearer invalid-token" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test"}'

# Monitor Cognito metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Cognito \
  --metric-name SignInSuccesses \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 300 --statistics Sum
```

### ContainersStack - Container and Load Balancer Monitoring

**What is Monitored:**
- ECS Fargate service health and performance
- Application Load Balancer metrics
- Container CPU and memory utilization
- Target group health checks

**Monitor ECS Service:**
```bash
# Check service status
aws ecs describe-services --cluster ContainersStack-cluster --services ContainersStack-service

# Monitor CPU utilization
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=ContainersStack-service Name=ClusterName,Value=ContainersStack-cluster \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 300 --statistics Average
```

**Test Load Balancer Health:**
```bash
# Get load balancer DNS from deployment output
export ALB_URL="http://your-alb-dns-name"

# Test application health
curl $ALB_URL/products

# Check target health
aws elbv2 describe-target-health --target-group-arn arn:aws:elasticloadbalancing:region:account:targetgroup/name

# Monitor request metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name RequestCount \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 300 --statistics Sum
```

### CICDStack - Pipeline and Build Monitoring

**What is Monitored:**
- CodePipeline execution status and duration
- CodeBuild project success/failure rates
- CodeCommit repository activity
- Manual approval workflow tracking

**Monitor Pipeline Activity:**
```bash
# List recent pipeline executions
aws codepipeline list-pipeline-executions --pipeline-name ProductsCatalogPipeline

# Get detailed execution info
aws codepipeline get-pipeline-execution \
  --pipeline-name ProductsCatalogPipeline \
  --pipeline-execution-id your-execution-id
```

**Track Build Performance:**
```bash
# List builds for project
aws codebuild list-builds-for-project --project-name your-project-name

# Get build details and logs
aws codebuild batch-get-builds --ids your-build-id
```

**Monitor Repository Activity:**
```bash
# Get repository information
aws codecommit get-repository --repository-name ProductsCatalog

# Check latest commits
aws codecommit get-branch --repository-name ProductsCatalog --branch-name main
```

## Performance Testing and Monitoring

### Load Testing Setup

**Install Testing Tools:**
```bash
# Ubuntu/Debian
sudo apt-get install apache2-utils

# macOS
brew install httpie

# Windows
# Download Apache Bench from Apache website
```

**Run Load Tests:**
```bash
# Basic load test
ab -n 1000 -c 10 $API_URL/products

# Monitor performance during test
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=your-function-name \
  --start-time $(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 60 --statistics Average,Maximum
```

### Error Monitoring and Troubleshooting

**Generate Test Errors:**
```bash
# Send invalid JSON to trigger errors
curl -X POST $API_URL/products \
  -H "Content-Type: application/json" \
  -d '{"invalid": json}'

# Send malformed requests
curl -X POST $API_URL/products/invalid-id \
  -H "Content-Type: application/json" \
  -d '{"price": "not-a-number"}'
```

**Monitor Error Logs:**
```bash
# Search for errors in Lambda logs
aws logs filter-log-events \
  --log-group-name "/aws/lambda/your-function-name" \
  --filter-pattern "ERROR"

# Get error metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Errors \
  --dimensions Name=FunctionName,Value=your-function-name \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 300 --statistics Sum
```

### Database Performance Monitoring

**Monitor DynamoDB Usage:**
```bash
# Check read capacity consumption
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name ConsumedReadCapacityUnits \
  --dimensions Name=TableName,Value=core_api_products \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 300 --statistics Sum

# Check write capacity consumption
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name ConsumedWriteCapacityUnits \
  --dimensions Name=TableName,Value=core_api_products \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 300 --statistics Sum
```

## CloudWatch Dashboards and Alerts

### Create Custom Dashboard

```bash
# Create a comprehensive monitoring dashboard
aws cloudwatch put-dashboard --dashboard-name "ProductCatalogDashboard" --dashboard-body '{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/Lambda", "Duration", "FunctionName", "CoreApi_GetProduct"],
          ["AWS/Lambda", "Invocations", "FunctionName", "CoreApi_GetProduct"],
          ["AWS/ApiGateway", "Count", "ApiName", "ProductsApi"],
          ["AWS/DynamoDB", "ConsumedReadCapacityUnits", "TableName", "core_api_products"]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-east-1",
        "title": "API Performance Overview"
      }
    }
  ]
}'
```

### Real-Time Log Monitoring

**Stream Logs in Real-Time:**
```bash
# Follow Lambda function logs
aws logs tail /aws/lambda/your-function-name --follow

# Filter logs for specific patterns
aws logs tail /aws/lambda/your-function-name --follow --filter-pattern "ERROR"

# Monitor multiple functions
aws logs tail /aws/lambda/CoreApi_GetProduct /aws/lambda/CoreApi_QueryProducts --follow
```

## Monitoring Features Summary

| Service | Metrics Available | Log Types | Testing Method |
|---------|------------------|-----------|----------------|
| **Lambda** | Duration, invocations, errors, throttling, concurrency | Function logs, error traces | Load testing, error injection |
| **API Gateway** | Request count, latency, cache hits/misses, 4XX/5XX errors | Access logs, execution logs | Cache testing, invalid requests |
| **DynamoDB** | Read/write capacity consumption, throttling | CloudWatch metrics only | High-volume operations |
| **S3** | Object operations, event notifications | Access logs, event logs | File upload triggers |
| **ElastiCache** | Cache hits/misses, memory usage | CloudWatch metrics | Cache performance testing |
| **Kinesis** | Record processing, stream metrics | Processing logs | Stream data injection |
| **ECS** | CPU/memory utilization, task health | Container logs | Load balancer testing |
| **Load Balancer** | Request metrics, target health | Access logs | Health check monitoring |
| **CodePipeline** | Execution status, stage duration | Build logs, pipeline logs | Code commits, manual triggers |
| **Cognito** | Authentication metrics | Sign-in logs | Auth failure testing |
| **KMS** | Key usage statistics | Encryption logs | Encrypted operations |

## Troubleshooting Common Issues

| Issue | Symptoms | How to Monitor | Solution |
|-------|----------|----------------|----------|
| **High Lambda Duration** | Slow API responses | CloudWatch Duration metric | Check logs for bottlenecks |
| **API Gateway Throttling** | 429 errors | 4XXError metric | Increase throttling limits |
| **DynamoDB Throttling** | Write/read failures | ThrottledRequests metric | Increase capacity or use auto-scaling |
| **Cache Misses** | Slow repeated requests | CacheMissCount metric | Check cache TTL settings |
| **Container Health Issues** | 503 errors from ALB | ECS service health | Check container logs and resource limits |
| **Pipeline Failures** | Build/deploy errors | CodeBuild logs | Review buildspec.yaml and permissions |

## Clean Up

**Important:** Always clean up resources to avoid ongoing charges

```bash
# Destroy any deployed stack
cdk destroy InitialApiStack
cdk destroy CoreApiStack
cdk destroy FullApiStack
cdk destroy ContainersStack
cdk destroy CICDStack

# Clean up CloudWatch dashboards
aws cloudwatch delete-dashboards --dashboard-names ProductCatalogDashboard
```

## Additional Resources

- [AWS CloudWatch User Guide](https://docs.aws.amazon.com/cloudwatch/)
- [Lambda Monitoring Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [API Gateway Monitoring](https://docs.aws.amazon.com/apigateway/latest/developerguide/monitoring_overview.html)
- [DynamoDB Monitoring](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/monitoring-cloudwatch.html)
- [ECS Monitoring](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/cloudwatch-metrics.html)