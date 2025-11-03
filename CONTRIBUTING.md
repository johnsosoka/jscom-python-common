# Contributing to jscom-python-common

Thank you for contributing to the JSCOM Python common library! This document provides guidelines for development, testing, and releasing changes.

## Development Setup

### Prerequisites

- Python 3.13+
- Poetry (Python dependency management)
- Git

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/johnsosoka/jscom-python-common.git
cd jscom-python-common

# Install dependencies with Poetry
poetry install --with dev

# Install pre-commit hooks
poetry run pre-commit install

# Verify setup
poetry run pytest
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
```

Branch naming conventions:
- `feature/` - New features
- `bugfix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring

### 2. Make Changes

Write clean, well-documented code following these principles:

- **Clarity Over Cleverness** - Code should be self-explanatory
- **Type Hints** - All function signatures must have type hints
- **Docstrings** - All public functions need comprehensive docstrings with examples
- **DRY Principle** - Don't repeat yourself
- **Single Responsibility** - Each function should do one thing well

### 3. Run Pre-commit Hooks

Pre-commit hooks run automatically before each commit:

```bash
# Manually run all hooks
poetry run pre-commit run --all-files
```

Hooks include:
- `ruff format` - Code formatting
- `ruff check` - Linting
- `mypy` - Type checking
- `pytest` - Test suite

### 4. Write Tests

All new code must have tests. Aim for 80%+ code coverage.

```bash
# Run tests
poetry run pytest

# Run with coverage report
poetry run pytest --cov=jscom_common --cov-report=term-missing

# Run specific test file
poetry run pytest tests/test_auth/test_cognito.py -v
```

**Test Guidelines:**
- Write unit tests for all functions
- Mock external dependencies (HTTP requests, AWS services)
- Test error cases and edge cases
- Use descriptive test names

### 5. Update Documentation

- Update README.md if adding new features
- Update CHANGELOG.md with your changes (under `[Unreleased]`)
- Add docstrings with examples to all new functions

### 6. Commit Changes

```bash
git add .
git commit -m "Brief description of changes"
```

Commit messages should:
- Be concise and descriptive
- Use imperative mood ("Add feature" not "Added feature")
- Reference issue numbers if applicable

### 7. Push and Create Pull Request

```bash
git push -u origin feature/your-feature-name

# Create PR using GitHub CLI
gh pr create --title "Feature: Your Feature Name" --body "Description of changes"
```

## Code Quality Standards

### Type Checking

All code must pass mypy type checking:

```bash
poetry run mypy jscom_common --ignore-missing-imports
```

### Linting

Code must pass ruff linting:

```bash
# Check formatting
poetry run ruff format --check .

# Check linting rules
poetry run ruff check .

# Auto-fix issues
poetry run ruff check . --fix
```

### Test Coverage

Maintain at least 80% test coverage:

```bash
poetry run pytest --cov=jscom_common --cov-fail-under=80
```

## Pull Request Process

1. **Create PR** - Submit pull request against `main` branch
2. **CI Checks** - GitHub Actions will run lint, type check, and tests
3. **Code Review** - Wait for code review and address feedback
4. **Merge** - Once approved and CI passes, PR will be merged

**PR Requirements:**
- All CI checks must pass
- Code review approval required
- No merge conflicts with main
- CHANGELOG.md updated

## Release Process

Releases are created via GitHub Actions workflow, which ensures all checks pass before tagging.

### Creating a Release

1. **Ensure main is ready**
   ```bash
   git checkout main
   git pull origin main
   ```

2. **Update CHANGELOG.md**
   - Move changes from `[Unreleased]` to new version section
   - Ensure all changes are documented

3. **Trigger Release Workflow**
   - Go to GitHub Actions tab
   - Select "Release" workflow
   - Click "Run workflow"
   - Enter version number (e.g., `0.2.0`)
   - Optionally add release notes
   - Click "Run workflow"

4. **Workflow validates**:
   - Version format is valid semver
   - Tag doesn't already exist
   - All CI checks passed on current commit
   - Creates commit with version bump
   - Creates and pushes git tag
   - Creates GitHub release

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.0.0) - Incompatible API changes
- **MINOR** (0.1.0) - New features, backward-compatible
- **PATCH** (0.0.1) - Bug fixes, backward-compatible

### What Triggers Each Version Type

**MAJOR version** (breaking changes):
- Removing or renaming functions
- Changing function signatures
- Removing parameters
- Changing return types incompatibly

**MINOR version** (new features):
- Adding new functions/modules
- Adding optional parameters
- Adding new response fields
- Deprecating (but not removing) functionality

**PATCH version** (bug fixes):
- Fixing bugs
- Performance improvements
- Documentation updates
- Internal refactoring

## Module Organization Guidelines

### When to Split Modules

Current modules are kept in single files. Consider splitting when:

- **File exceeds ~300 lines** - See note in `jscom_common/dynamodb/helpers.py`
- **Clear functional separation** - E.g., pagination vs batch operations
- **Independent testing** - Functions can be tested in isolation

### Adding New Modules

When adding a new module:

1. Create directory: `jscom_common/new_module/`
2. Add `__init__.py` with public exports
3. Create implementation file(s)
4. Write comprehensive tests in `tests/test_new_module/`
5. Update README.md with usage examples
6. Update CHANGELOG.md

## Common Tasks

### Running Checks Locally

```bash
# All checks (what CI runs)
poetry run ruff format --check .
poetry run ruff check .
poetry run mypy jscom_common --ignore-missing-imports
poetry run pytest --cov=jscom_common --cov-fail-under=80

# Or use pre-commit
poetry run pre-commit run --all-files
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
```

### Debugging Test Failures

```bash
# Run tests with verbose output
poetry run pytest -vv

# Run specific test
poetry run pytest tests/test_auth/test_cognito.py::TestValidateJWTToken::test_success -vv

# Run tests with print statements
poetry run pytest -s

# Run tests with debugger
poetry run pytest --pdb
```

## Getting Help

- **Questions**: Open a GitHub issue with the `question` label
- **Bugs**: Open a GitHub issue with the `bug` label
- **Feature Requests**: Open a GitHub issue with the `enhancement` label

## Code of Conduct

- Be respectful and professional
- Focus on constructive feedback
- Help others learn and grow
- Keep discussions on-topic

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
