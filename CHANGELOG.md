# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-11-02

### Added

- Initial release of jscom-python-common shared library
- **Authentication Module** (`jscom_common.auth`)
  - `get_jwks()` - Fetch and cache JWKS from AWS Cognito
  - `validate_jwt_token()` - Validate JWT tokens from API Gateway events
  - Support for environment variable configuration
  - JWKS caching to reduce HTTP requests

- **Models Module** (`jscom_common.models`)
  - `ApiResponse[T]` - Generic API response wrapper supporting both status-code and success-boolean patterns
  - `PaginatedResponse[T]` - Standardized paginated list responses with cursor tokens

- **DynamoDB Module** (`jscom_common.dynamodb`)
  - `encode_pagination_token()` - Encode DynamoDB LastEvaluatedKey to base64
  - `decode_pagination_token()` - Decode base64 token to ExclusiveStartKey
  - `pydantic_to_dynamodb()` - Convert Pydantic models to DynamoDB items (excludes None)
  - `dynamodb_to_pydantic()` - Convert DynamoDB items to Pydantic models

- Comprehensive test coverage (80%+)
  - Unit tests for all modules
  - Mock-based tests for HTTP requests and JWT validation
  - Validation error handling tests

- Complete documentation
  - README with installation instructions and usage examples
  - Migration guide for existing projects
  - API reference documentation
  - Development guidelines

### Dependencies

- Python >= 3.13
- boto3 >= 1.28.0
- pydantic >= 2.0
- python-jose[cryptography] >= 3.3.0
- requests >= 2.31.0
- aws-lambda-powertools >= 2.0.0

## Migration Notes

### From Local Implementations

This release extracts commonly duplicated code from jscom-contact-services, jscom-newsletter-services, and jscom-homelab-services. Projects using local implementations should:

1. Add dependency: `git+https://github.com/johnsosoka/jscom-python-common.git@v0.1.0`
2. Update imports to use `jscom_common` modules
3. Remove local copies of JWT validation, response models, and DynamoDB helpers
4. Test thoroughly in staging before production deployment

### Breaking Changes

None - this is the initial release.

---

## Release Process

### Version Numbering

- **MAJOR**: Incompatible API changes
- **MINOR**: New features (backward-compatible)
- **PATCH**: Bug fixes (backward-compatible)

### Creating a Release

1. Update version in `pyproject.toml`
2. Update this CHANGELOG with release notes
3. Commit: `git commit -m "Release vX.Y.Z"`
4. Tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z: Description"`
5. Push: `git push origin vX.Y.Z && git push origin main`

[Unreleased]: https://github.com/johnsosoka/jscom-python-common/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/johnsosoka/jscom-python-common/releases/tag/v0.1.0
