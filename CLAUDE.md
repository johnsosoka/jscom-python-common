# CLAUDE.md

## Project Overview

**jscom-python-common** is a shared Python library that provides common functionality across all JSCOM Python serverless projects, eliminating code duplication and ensuring consistency.

**Repository:** https://github.com/johnsosoka/jscom-python-common
**Type:** Python Library (pip-installable from GitHub)
**Python Version:** 3.13+
**Package Manager:** Poetry
**Distribution:** GitHub releases with semantic versioning

## Purpose & Architecture

### Core Functionality

This library provides three main modules:

1. **`jscom_common.auth`** - Cognito JWT token validation
   - Fetches and caches JWKS from AWS Cognito
   - Validates JWT tokens from API Gateway events
   - Supports environment variable configuration

2. **`jscom_common.models`** - Standardized API response models
   - `ApiResponse[T]` - Generic API response wrapper
   - `PaginatedResponse[T]` - Paginated list responses with cursor tokens
   - Pydantic-based for type safety

3. **`jscom_common.dynamodb`** - DynamoDB utilities
   - Pagination token encoding/decoding (base64)
   - Bidirectional Pydantic ↔ DynamoDB conversions

### Consumer Projects

- **jscom-contact-services** - Contact form API (planned migration)
- **jscom-newsletter-services** - Newsletter subscription API (planned migration)
- **jscom-homelab-services** - Homelab management API (planned migration)

### Design Principles

- **DRY** - Single source of truth for shared functionality
- **Type Safety** - Full mypy type checking, Pydantic models
- **Well Tested** - 80%+ code coverage requirement
- **Version Pinning** - Consumers pin to specific releases for stability

## Development Workflow

### Setup

```bash
# Clone repository
git clone https://github.com/johnsosoka/jscom-python-common.git
cd jscom-python-common

# Install dependencies
poetry install --with dev

# Install pre-commit hooks (CRITICAL!)
poetry run pre-commit install

# Verify setup
poetry run pytest
```

### Feature Development

```bash
# Create feature branch
git checkout main
git pull origin main
git checkout -b feature/your-feature-name

# Make changes
# Write tests (required!)
# Run pre-commit hooks
poetry run pre-commit run --all-files

# Commit and push
git add .
git commit -m "feat: add new feature"
git push -u origin feature/your-feature-name

# Create PR
gh pr create --title "Feature: Your Feature Name" --body "Description"
```

### Code Quality Requirements

All code must pass:
- ✅ **ruff format** - Code formatting
- ✅ **ruff check** - Linting
- ✅ **mypy** - Type checking (--ignore-missing-imports)
- ✅ **pytest** - Test suite with 80%+ coverage

**Run all checks:**
```bash
poetry run pre-commit run --all-files
```

## Release Process

### Overview

Releases use a two-stage GitHub Actions workflow with manual approval:

**Stage 1: Release Preparation** (`release-prep.yml`)
1. Validates prerequisites (version format, CI status, no existing tag)
2. Creates release branch with version updates
3. Creates PR and displays next steps

**Stage 2: Release Finalization** (`release-finalize.yml`)
1. Automatically triggers when release PR is merged
2. Pauses for manual approval via GitHub Environment
3. Creates git tag and GitHub Release after approval

**Note:** Auto-cleanup workflow runs on preparation failure.

### Creating a Release

**Pre-Release Checklist:**
- [ ] All changes merged to main
- [ ] CHANGELOG.md updated under `[Unreleased]`
- [ ] CI checks passing on main
- [ ] Version number decided (MAJOR.MINOR.PATCH)
- [ ] GitHub Environment `release` configured (one-time setup)

**Steps:**

1. **Update CHANGELOG.md:**
   ```markdown
   ## [Unreleased]

   ### Added
   - New feature description

   ### Fixed
   - Bug fix description
   ```

2. **Commit and push:**
   ```bash
   git add CHANGELOG.md
   git commit -m "docs: update changelog for v0.2.0"
   git push origin main
   ```

3. **Trigger Release Preparation:**
   - Navigate to: [Actions → Release Preparation](https://github.com/johnsosoka/jscom-python-common/actions/workflows/release-prep.yml)
   - Click "Run workflow"
   - Enter version (e.g., `0.2.0` - no 'v' prefix)
   - Click "Run workflow"

4. **Review and merge PR:**
   - PR will be created automatically (~30 seconds)
   - Review the version updates
   - Merge PR (squash merge) - no CI checks expected

5. **Approve deployment:**
   - Release Finalization workflow triggers automatically
   - Navigate to the workflow run
   - Click "Review deployments"
   - Approve the `release` environment
   - Tag and release created automatically

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR (X.0.0)** - Breaking changes (incompatible API changes)
  - Removing/renaming functions
  - Changing function signatures
  - Removing parameters
  - Changing return types incompatibly

- **MINOR (0.X.0)** - New features (backward-compatible)
  - Adding new functions/modules
  - Adding optional parameters
  - Adding new response fields
  - Deprecating (not removing) functionality

- **PATCH (0.0.X)** - Bug fixes (backward-compatible)
  - Fixing bugs
  - Performance improvements
  - Documentation updates
  - Internal refactoring

### Troubleshooting Releases

**Common Issues:**

1. **No CI checks on release PR:**
   - This is expected (github-actions[bot] limitation)
   - CI validated before PR creation, safe to merge

2. **Release branch already exists:**
   - Workflow auto-deletes, but if needed: `git push origin --delete release/v0.1.0`

3. **Forgot to approve deployment:**
   - Navigate to Actions → Find "Release Finalization" run
   - Click "Review deployments" → Approve

4. **Release Finalization doesn't trigger:**
   - Verify PR was merged (not just closed)
   - Verify branch name started with `release/`

See [CONTRIBUTING.md - Release Troubleshooting](./CONTRIBUTING.md#release-troubleshooting) for comprehensive guide.

## Testing

### Running Tests

```bash
# All tests
poetry run pytest

# With coverage
poetry run pytest --cov=jscom_common --cov-report=term-missing

# Specific test file
poetry run pytest tests/test_auth/test_cognito.py -v

# Check 80% threshold
poetry run pytest --cov=jscom_common --cov-fail-under=80
```

### Test Guidelines

- **Unit tests** for all functions
- **Mock external dependencies** (HTTP, AWS services)
- **Test error cases** and edge cases
- **Descriptive test names** - Clear what's being tested
- **80%+ coverage** - Required for CI

### Test Structure

```
tests/
├── test_auth/
│   └── test_cognito.py      # JWT validation tests
├── test_dynamodb/
│   └── test_helpers.py      # DynamoDB utility tests
└── test_models/
    └── test_api_response.py # Pydantic model tests
```

## Integration with Consumer Projects

### Installation in Consumer Projects

**requirements.txt:**
```txt
# Pin to specific version (recommended)
git+https://github.com/johnsosoka/jscom-python-common.git@v0.1.0

# Or use main (not recommended for production)
git+https://github.com/johnsosoka/jscom-python-common.git@main
```

### Migration Pattern

**Before (duplicated code in Lambda):**
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

**After (using library):**
```python
from jscom_common.auth import validate_jwt_token

# JWT validation is now a single import!
```

### Usage Examples

**Cognito JWT Authentication:**
```python
from jscom_common.auth import validate_jwt_token

def lambda_handler(event, context):
    try:
        claims = validate_jwt_token(event)  # Uses env vars
        username = claims.get("cognito:username")
        # Business logic...
    except Exception as e:
        return {"statusCode": 401, "body": "Unauthorized"}
```

**API Response Models:**
```python
from jscom_common.models import ApiResponse, PaginatedResponse

# Simple response
response = ApiResponse(
    status_code=200,
    data={"user_id": "123"},
    message="Success"
)

# Paginated response
response = PaginatedResponse(
    status_code=200,
    items=[item1, item2],
    next_token=encode_pagination_token({"pk": "123"}),
    message="Success"
)
```

**DynamoDB Helpers:**
```python
from jscom_common.dynamodb import (
    encode_pagination_token,
    decode_pagination_token,
    pydantic_to_dynamodb,
    dynamodb_to_pydantic
)

# Pagination
token = encode_pagination_token({"pk": "USER#123", "sk": "ITEM#456"})
last_key = decode_pagination_token(token)

# Model conversion
item_dict = pydantic_to_dynamodb(pydantic_model)
pydantic_model = dynamodb_to_pydantic(item_dict, MyModel)
```

## CI/CD

### GitHub Actions Workflows

**1. Code Quality & Tests (ci.yml)**
- Triggers: PR to main, push to main
- Parallel jobs:
  - Lint (ruff)
  - Type check (mypy)
  - Test suite (pytest with 80% coverage)
- Duration: ~45-48 seconds
- Required to pass for PR merge

**2. Release (release.yml)**
- Trigger: Manual workflow dispatch
- Steps:
  - Validate prerequisites
  - Create release branch
  - Create and merge PR
  - Create git tag and GitHub Release
  - Auto-cleanup on failure
- Duration: 2-3 minutes

**3. Release Cleanup (release-cleanup.yml)**
- Trigger: When Release workflow fails
- Actions:
  - Close open release PRs
  - Delete orphaned release branches
  - Delete orphaned tags (if no release exists)

### Workflow Diagrams

See [README.md - Workflow Diagrams](./README.md#workflow-diagrams) for visual representations of:
- Release & Tagging Flow
- CI/CD Workflow
- Installation & Integration Flow
- Development Workflow

## Common Operations

### Adding a New Module

```bash
# 1. Create module structure
mkdir jscom_common/new_module
touch jscom_common/new_module/__init__.py
touch jscom_common/new_module/implementation.py

# 2. Write implementation with type hints and docstrings
# 3. Export public API in __init__.py

# 4. Create tests
mkdir tests/test_new_module
touch tests/test_new_module/test_implementation.py

# 5. Write comprehensive tests

# 6. Update documentation
# - README.md (usage examples)
# - CHANGELOG.md (under [Unreleased])

# 7. Create PR
```

### Updating Dependencies

```bash
# Update single dependency
poetry update requests

# Update all dependencies
poetry update

# Add new dependency
poetry add new-package

# Add new dev dependency
poetry add --group dev new-package

# Update and test
poetry run pytest
```

### Debugging Test Failures

```bash
# Verbose output
poetry run pytest -vv

# Specific test
poetry run pytest tests/test_auth/test_cognito.py::TestValidateJWTToken::test_success -vv

# With print statements
poetry run pytest -s

# With debugger
poetry run pytest --pdb
```

## Project Statistics

- **Lines of Code:** ~823 total (373 source, 450 tests)
- **Test Coverage:** 80%+ required
- **Modules:** 3 (auth, models, dynamodb)
- **Dependencies:** boto3, pydantic, python-jose, requests, aws-lambda-powertools
- **Python Version:** 3.13+

## Best Practices

### When to Add Code to This Library

Only add code when:
- ✅ Used by 2+ JSCOM projects (avoid premature abstraction)
- ✅ Stable interface (not changing frequently)
- ✅ Well-tested (80%+ coverage)
- ✅ Properly typed (mypy passes)
- ✅ Well-documented (docstrings + README examples)

### When NOT to Add Code

Avoid adding:
- ❌ Project-specific business logic
- ❌ Experimental/unstable code
- ❌ Code used by only one project
- ❌ Frequently changing interfaces

### Version Update Strategy for Consumers

When a new version is released:

1. **Test in staging:**
   ```bash
   # Update requirements.txt
   git+https://github.com/johnsosoka/jscom-python-common.git@v0.2.0

   # Deploy to staging
   cd terraform
   terraform apply -var-file=staging.tfvars
   ```

2. **Verify functionality:**
   - Run integration tests
   - Check CloudWatch logs
   - Test affected endpoints

3. **Deploy to production:**
   ```bash
   terraform apply -var-file=production.tfvars
   ```

## Quick Reference

**Setup:**
```bash
poetry install --with dev
poetry run pre-commit install
```

**Run checks:**
```bash
poetry run pre-commit run --all-files
```

**Run tests:**
```bash
poetry run pytest --cov=jscom_common --cov-report=term-missing
```

**Create release:**
- Update CHANGELOG.md
- Navigate to GitHub Actions → Release workflow
- Enter version number
- Click "Run workflow"

**Troubleshooting:**
- See [CONTRIBUTING.md - Release Troubleshooting](./CONTRIBUTING.md#release-troubleshooting)
- Check workflow logs in GitHub Actions
- Review [Workflow Diagrams](./README.md#workflow-diagrams)

## Documentation

- **README.md** - User-facing documentation, usage examples, workflow diagrams
- **CONTRIBUTING.md** - Developer guidelines, detailed release process, troubleshooting
- **CHANGELOG.md** - Version history and release notes
- **CLAUDE.md** (this file) - Project overview and operational guide

## Support

- **Issues:** https://github.com/johnsosoka/jscom-python-common/issues
- **Workflow Logs:** GitHub Actions tab
- **CI Status:** Check badges in README.md
