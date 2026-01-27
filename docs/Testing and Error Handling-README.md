# Testing Guide - Testing and Error Handling

Learn how to test AWS Lambda functions and DynamoDB operations locally using mocking frameworks. This guide covers unit testing, integration testing, and best practices for serverless application testing.

## What You Will Learn

This testing suite demonstrates:
- **Unit Testing** Lambda functions without AWS dependencies
- **DynamoDB Mocking** using Moto library for local testing
- **Integration Testing** with real AWS services

## Prerequisites

**Required Tools:**
- Python 3.12+
- pytest or unittest
- AWS CLI configured (for integration tests)
- Virtual environment activated

For detailed setup instructions, see [Project Setup](../README.md).

## Test Structure Overview

```
tests/
├── unit/                         # Unit tests (no AWS dependencies)
│   ├── initial_api/              # Initial API Stack tests
│   │   ├── test_get_product_lambda.py
│   │   ├── test_query_products_lambda.py
│   │   ├── test_insert_product_lambda.py
│   │   ├── test_update_product_lambda.py
│   │   ├── test_delete_product_lambda.py
│   │   └── test_options_lambda.py
│   ├── core_api/                 # Core API Stack tests (DynamoDB)
│   │   ├── test_get_product_lambda.py
│   │   ├── test_query_products_lambda.py
│   │   ├── test_insert_product_lambda.py
│   │   ├── test_update_product_lambda.py
│   │   ├── test_delete_product_lambda.py
│   │   ├── test_options_lambda.py
│   │   ├── test_products_db_moto.py
│   │   └── testing_utils.py
│   ├── full_api/                 # Full API Stack tests
│   │   ├── test_generate_upload_url.py
│   │   └── test_generate_download_url.py
│   └── containers/               # Container Stack tests
│       ├── test_products_db_moto.py
│       └── test_products_db_patch.py
└── integration/                  # Integration tests (real AWS)
    ├── test_products.py
    └── add_products.py
```

## Quick Start

### Step 1: Set Up Testing Environment
```bash
# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate.bat  # Windows

# Install testing dependencies
pip install -r requirements-dev.txt
```

### Step 2: Run Unit Tests
```bash
# Run all unit tests
python -m pytest tests/unit/ -v

# Run specific stack tests
python -m pytest tests/unit/core_api/ -v

# Run single test file
python -m pytest tests/unit/core_api/test_get_product_lambda.py -v
```

### Step 3: Run Integration Tests
```bash
# Deploy stack first (required for integration tests)
cdk deploy CoreApiStack
```
Save the `CoreApiStack.ProductsApiUrl` and `CoreApiStack.UIUrl` from the deployment output for testing.



# Run integration tests
python -m pytest tests/integration/ -v
```
## Clean Up

**Important:** Always clean up to avoid ongoing charges
```bash
cdk destroy CoreApiStack
```


## Running Tests

### Using pytest 

```bash
# Install pytest
pip install pytest

# Run all tests with verbose output
pytest tests/ -v

# Run tests with coverage report
pytest tests/ --cov=aws_developer_sample_project --cov-report=html

# Run specific test patterns
pytest tests/ -k "test_get_product" -v

# Run tests in parallel
pytest tests/ -n auto
```

### Using unittest

```bash
# Run all unit tests
python -m unittest discover tests/unit -v

# Run specific test file
python -m unittest tests.unit.core_api.test_get_product_lambda -v

# Run single test method
python -m unittest tests.unit.core_api.test_get_product_lambda.TestGetProducts.test_get_existing_product -v
```


## Debugging Tests

### View Test Output
```bash
# Run with detailed output
pytest tests/ -v -s

# Show print statements
pytest tests/ -v -s --capture=no
```

### Debug Failed Tests
```bash
# Stop on first failure
pytest tests/ -x

# Enter debugger on failure
pytest tests/ --pdb

# Run last failed tests only
pytest tests/ --lf
```


## Troubleshooting

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| ImportError | Module path issues | Check PYTHONPATH and imports |
| Moto not mocking | Missing @moto.mock_aws decorator | Add decorator to test class/method |
| Tests fail randomly | Shared state between tests | Ensure proper setUp/tearDown |
| Slow tests | Using real AWS instead of mocks | Verify moto decorators are applied |
| Coverage issues | Tests not finding source code | Check coverage configuration |

## Additional Resources

- [Moto Documentation](https://docs.getmoto.org/)
- [pytest Documentation](https://docs.pytest.org/)
- [AWS Lambda Testing Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/testing-guide.html)
- [Python unittest Documentation](https://docs.python.org/3/library/unittest.html)


