# jscom-python-common

[![CI](https://github.com/johnsosoka/jscom-python-common/actions/workflows/ci.yml/badge.svg)](https://github.com/johnsosoka/jscom-python-common/actions/workflows/ci.yml)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Shared utilities and models for johnsosoka.com Python Lambda functions.

## Overview

This library provides common functionality across all JSCOM Python serverless projects, eliminating code duplication and ensuring consistency across services. It includes:

- **Cognito JWT Authentication** - Validate AWS Cognito JWT tokens in Lambda functions
- **API Response Models** - Standardized Pydantic models for API responses
- **DynamoDB Helpers** - Utilities for pagination and Pydantic model conversions

## Installation

Install directly from GitHub using pip with a specific version tag:

```bash
pip install "git+https://github.com/johnsosoka/jscom-python-common.git@v0.1.0"
```

Or install the latest version from main (not recommended for production):

```bash
pip install "git+https://github.com/johnsosoka/jscom-python-common.git@main"
```

### Requirements

- Python 3.13+
- boto3 >= 1.28.0
- pydantic >= 2.0
- python-jose[cryptography] >= 3.3.0
- requests >= 2.31.0
- aws-lambda-powertools >= 2.0.0

## Usage

### Cognito JWT Authentication

Validate JWT tokens from AWS Cognito User Pools in Lambda authorizers or API Gateway integrations.

```python
from jscom_common.auth import validate_jwt_token
from aws_lambda_powertools import Logger

logger = Logger()

def lambda_handler(event, context):
    try:
        # Validate JWT token from Authorization header
        claims = validate_jwt_token(
            event,
            region="us-west-2",
            user_pool_id="us-west-2_YourPoolId",
            app_client_id="your-app-client-id"
        )

        # Access user information
        username = claims.get("cognito:username")
        email = claims.get("email")

        logger.info(f"Authenticated user: {username}")

        # Your business logic here
        return {"statusCode": 200, "body": "Success"}

    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        return {"statusCode": 401, "body": "Unauthorized"}
```

**Environment Variables:**

The validation function can read from environment variables if parameters aren't provided:

- `COGNITO_REGION` - AWS region (defaults to "us-west-2")
- `COGNITO_USER_POOL_ID` - Cognito User Pool ID
- `COGNITO_APP_CLIENT_ID` - Cognito App Client ID

```python
# Using environment variables (recommended)
claims = validate_jwt_token(event)
```

### API Response Models

Use standardized response models for consistent API responses across all JSCOM services.

#### Status-Code Pattern

Used in contact-services and newsletter-services:

```python
from jscom_common.models import ApiResponse
from pydantic import BaseModel

class User(BaseModel):
    id: str
    name: str
    email: str

# Success response
user = User(id="123", name="John", email="john@example.com")
response = ApiResponse[User](status=200, data=user)

# Error response
response = ApiResponse[None](status=404, error="User not found")

# Return from Lambda
return response.model_dump()
```

#### Success-Boolean Pattern

Used in homelab-services:

```python
from jscom_common.models import ApiResponse

# Success response
response = ApiResponse[User](
    success=True,
    data=user,
    message="User retrieved successfully"
)

# Error response
response = ApiResponse[None](
    success=False,
    error="Operation failed",
    message="Invalid input"
)
```

#### Paginated Responses

For list endpoints with cursor-based pagination:

```python
from jscom_common.models import PaginatedResponse

users = [user1, user2, user3]
response = PaginatedResponse[User](
    items=users,
    count=len(users),
    next_token="eyJpZCI6IjEyMyJ9"  # Base64-encoded pagination token
)

# Last page (no more items)
response = PaginatedResponse[User](
    items=[last_user],
    count=1,
    next_token=None
)
```

### DynamoDB Helpers

Utilities for working with DynamoDB pagination and Pydantic model conversions.

#### Pagination Token Encoding/Decoding

```python
from jscom_common.dynamodb import encode_pagination_token, decode_pagination_token
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('my-table')

# Query with pagination
response = table.scan(Limit=50)
items = response['Items']

# Encode LastEvaluatedKey for API response
next_token = None
if 'LastEvaluatedKey' in response:
    next_token = encode_pagination_token(response['LastEvaluatedKey'])

# In subsequent request, decode token
if next_token:
    start_key = decode_pagination_token(next_token)
    response = table.scan(Limit=50, ExclusiveStartKey=start_key)
```

#### Pydantic Model Conversions

```python
from jscom_common.dynamodb import pydantic_to_dynamodb, dynamodb_to_pydantic
from pydantic import BaseModel
import boto3

class User(BaseModel):
    id: str
    name: str
    email: str | None = None

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('users')

# Convert Pydantic model to DynamoDB item (excludes None values)
user = User(id="123", name="John", email=None)
item = pydantic_to_dynamodb(user)
table.put_item(Item=item)

# Convert DynamoDB item to Pydantic model
response = table.get_item(Key={'id': '123'})
user = dynamodb_to_pydantic(response['Item'], User)
print(user.name)  # "John"
```

## Module Reference

### `jscom_common.auth`

- `get_jwks(region, user_pool_id)` - Fetch and cache JWKS from Cognito
- `validate_jwt_token(event, region, user_pool_id, app_client_id)` - Validate JWT token from API Gateway event

### `jscom_common.models`

- `ApiResponse[T]` - Generic API response wrapper (supports both patterns)
- `PaginatedResponse[T]` - Paginated list response with cursor tokens

### `jscom_common.dynamodb`

- `encode_pagination_token(last_key)` - Encode DynamoDB LastEvaluatedKey to base64
- `decode_pagination_token(token)` - Decode base64 token to ExclusiveStartKey
- `pydantic_to_dynamodb(model)` - Convert Pydantic model to DynamoDB item
- `dynamodb_to_pydantic(item, model_class)` - Convert DynamoDB item to Pydantic model

## Migration Guide

### Migrating from Local Implementations

If your project has local copies of these utilities, follow these steps:

1. **Add Dependency**

   Update `requirements.txt`:
   ```txt
   git+https://github.com/johnsosoka/jscom-python-common.git@v0.1.0
   ```

2. **Update Imports**

   ```python
   # Before
   from models.response_models import ApiResponse, PaginatedResponse
   from utils.dynamodb_helper import encode_pagination_token

   # After
   from jscom_common.models import ApiResponse, PaginatedResponse
   from jscom_common.dynamodb import encode_pagination_token
   ```

3. **Remove Duplicated Code**

   Delete local files:
   - `app/models/response_models.py` (if only generic models)
   - `app/utils/dynamodb_helper.py`
   - JWT validation code from Lambda functions

4. **Test Thoroughly**

   ```bash
   # Run existing tests
   python -m pytest -v

   # Test in staging environment
   cd terraform
   terraform apply
   ```

### Example Migration: contact-services

Before:
```python
# contact-admin Lambda
def get_jwks():
    global _jwks_cache
    if _jwks_cache is None:
        # ... 20 lines of code ...
    return _jwks_cache

def validate_jwt_token(event):
    # ... 60 lines of code ...
    pass
```

After:
```python
from jscom_common.auth import validate_jwt_token

# JWT validation is now a single import!
```

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/johnsosoka/jscom-python-common.git
cd jscom-python-common

# Install dependencies
poetry install --with dev

# Install pre-commit hooks
poetry run pre-commit install
```

### Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality:

```bash
# Hooks run automatically on git commit
git commit -m "Your message"

# Run manually on all files
poetry run pre-commit run --all-files
```

Hooks include:
- `ruff format` - Code formatting
- `ruff check` - Linting with auto-fix
- `mypy` - Type checking
- `pytest` - Test suite (fail fast)

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=jscom_common --cov-report=term-missing

# Run specific test file
poetry run pytest tests/test_auth/test_cognito.py -v

# Check coverage threshold (80%)
poetry run pytest --cov=jscom_common --cov-fail-under=80
```

### Code Quality

```bash
# Format code
poetry run ruff format .

# Lint code
poetry run ruff check .

# Type checking
poetry run mypy jscom_common --ignore-missing-imports

# Run all checks (what CI runs)
poetry run pre-commit run --all-files
```

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed development guidelines, including:
- Development workflow
- Code quality standards
- Pull request process
- Release process

## Versioning and Releases

This library follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality in a backward-compatible manner
- **PATCH** version for backward-compatible bug fixes

### Creating a Release

Releases are created via GitHub Actions workflow to ensure all checks pass:

1. **Update CHANGELOG.md** - Document changes under `[Unreleased]`
2. **Commit and push to main**
3. **Trigger Release Workflow**:
   - Go to GitHub Actions tab
   - Select "Release" workflow
   - Click "Run workflow"
   - Enter version number (e.g., `0.2.0`)
   - Click "Run workflow"

The workflow will:
- Validate version format and CI checks
- Update `pyproject.toml` and `CHANGELOG.md`
- Create and push git tag
- Create GitHub release

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed release process.

### Using Specific Versions

Always pin to specific versions in production:

```txt
# Good - pinned version
git+https://github.com/johnsosoka/jscom-python-common.git@v0.1.0

# Avoid in production - uses latest
git+https://github.com/johnsosoka/jscom-python-common.git@main
```

## Projects Using This Library

- [jscom-contact-services](https://github.com/johnsosoka/jscom-contact-services) - Contact form API
- [jscom-newsletter-services](https://github.com/johnsosoka/jscom-newsletter-services) - Newsletter subscription API
- [jscom-homelab-services](https://github.com/johnsosoka/jscom-homelab-services) - Homelab management API (planned)

## Contributing

This is a private library for JSCOM projects. When adding new shared functionality:

1. Ensure it's used by 2+ projects (avoid premature abstraction)
2. Write comprehensive tests (80%+ coverage)
3. Update this README with usage examples
4. Follow existing code style and patterns
5. Create a new version tag after merging

## License

MIT License - See LICENSE file for details.

## Support

For issues or questions, open an issue at:
https://github.com/johnsosoka/jscom-python-common/issues
