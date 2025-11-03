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

**⚠️ CRITICAL:** Always run pre-commit hooks before pushing to catch issues early!

Pre-commit hooks run automatically before each commit (if installed):

```bash
# First time only: Install hooks
poetry run pre-commit install

# Verify installation
ls -la .git/hooks/pre-commit  # File should exist

# Hooks now run automatically
git commit -m "Your message"  # Hooks run here
```

**Best Practice - Run before pushing:**
```bash
# Always run this before creating a PR
poetry run pre-commit run --all-files

# If any checks fail:
# 1. Review the failures
# 2. Fix the issues (many auto-fix)
# 3. Stage and commit the fixes
git add .
git commit -m "Fix pre-commit issues"
```

**What the hooks check:**
- ✅ `ruff format` - Code formatting (auto-fix)
- ✅ `ruff check` - Linting with auto-fix
- ✅ `mypy` - Type checking (must fix manually)
- ✅ `pytest` - Test suite (fail fast on first error)
- ✅ YAML/TOML validation, trailing whitespace, large files

**If CI fails but local passes:**
```bash
# Ensure you're running the same versions
poetry update

# Run exactly what CI runs
poetry run ruff format --check .
poetry run ruff check .
poetry run mypy jscom_common --ignore-missing-imports
poetry run pytest --cov=jscom_common --cov-fail-under=80
```

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

Releases use a two-stage GitHub Actions workflow that requires manual approval. The **Release Preparation** workflow creates a PR with version updates, then the **Release Finalization** workflow (triggered after PR merge) creates the tag and GitHub Release after manual approval via GitHub Environments.

### Pre-Release Checklist

Before triggering a release:

- [ ] All desired changes are merged to `main`
- [ ] CHANGELOG.md is updated with changes under `[Unreleased]`
- [ ] All CI checks are passing on `main`
- [ ] No existing `release/vX.Y.Z` branches for this version
- [ ] Decided on version number (MAJOR.MINOR.PATCH)
- [ ] Reviewed that consuming projects can handle any changes

### Creating a Release

1. **Ensure main is ready**
   ```bash
   git checkout main
   git pull origin main
   ```

2. **Update CHANGELOG.md**
   ```markdown
   ## [Unreleased]

   ### Added
   - New feature description

   ### Fixed
   - Bug fix description
   ```

3. **Commit and push to main**
   ```bash
   git add CHANGELOG.md
   git commit -m "docs: update changelog for v0.2.0"
   git push origin main
   ```

4. **Trigger Release Preparation Workflow**
   - Navigate to: [GitHub Actions → Release Preparation](https://github.com/johnsosoka/jscom-python-common/actions/workflows/release-prep.yml)
   - Click "Run workflow"
   - Enter version number (e.g., `0.2.0` - no 'v' prefix)
   - Leave release notes empty (will extract from CHANGELOG)
   - Click "Run workflow"

5. **Review and Merge Release PR**
   - The workflow creates a PR with version updates
   - Review the PR (no CI checks will run - this is expected)
   - Merge the PR when ready (squash merge)

6. **Approve Release Deployment**
   - The Release Finalization workflow triggers automatically
   - Navigate to the workflow run in GitHub Actions
   - Click "Review deployments"
   - Approve the `release` environment
   - Tag and GitHub Release will be created automatically

### What the Workflow Does

The release process consists of two workflows:

#### Workflow 1: Release Preparation (`release-prep.yml`)

**1. Validation Phase:**
- ✅ Validates version format (must be semver: `X.Y.Z`)
- ✅ Checks tag doesn't already exist
- ✅ Verifies CI checks passed on current commit

**2. Preparation Phase:**
- 🔍 Checks if `release/vX.Y.Z` branch already exists
- 🗑️ Deletes existing release branch if found (from previous failed attempt)
- 📝 Updates `pyproject.toml` with new version
- 📅 Updates `CHANGELOG.md` with release date
- 🌿 Creates `release/vX.Y.Z` branch
- 💾 Commits changes
- ⬆️ Pushes branch to origin

**3. PR Creation:**
- 📬 Creates PR to merge release branch into `main`
- 📋 Displays summary with next steps

**Duration:** ~30 seconds

#### Workflow 2: Release Finalization (`release-finalize.yml`)

**Triggered automatically when release PR is merged to main**

**1. Release Detection:**
- 🔍 Detects that a `release/vX.Y.Z` branch was merged
- 📝 Extracts version number from branch name
- 🏷️ Determines if this is a pre-release (alpha, beta, rc)

**2. Approval Gate:**
- ⏸️ Pauses for manual approval via GitHub Environment
- 👤 Requires designated reviewer to approve deployment
- 🔐 Uses `release` environment protection

**3. Tag and Release Creation:**
- 📝 Extracts CHANGELOG notes for this version
- 🔖 Creates git tag `vX.Y.Z`
- ⬆️ Pushes tag to origin
- 📦 Creates GitHub Release with CHANGELOG notes
- ✅ Marks as pre-release if version contains `-`, `alpha`, `beta`, or `rc`

**Duration:** ~1 minute (after approval)

#### Cleanup on Failure

If the **Release Preparation** workflow fails, a separate cleanup workflow automatically:
- Closes any open release PRs
- Deletes orphaned release branches
- Deletes orphaned tags (if no GitHub release exists)

**Total Duration:** ~2 minutes + PR review time + approval time

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

## Release Troubleshooting

### Problem: "non-fast-forward" error when pushing release branch

**Symptom:**
```
! [rejected]        release/v0.1.0 -> release/v0.1.0 (non-fast-forward)
error: failed to push some refs
hint: Updates were rejected because the tip of your current branch is behind
```

**Cause:** Release branch already exists from a previous failed workflow run.

**Solution:**
The workflow now automatically detects and deletes existing release branches. If you still encounter this error:

```bash
# Manually delete the orphaned branch
git push origin --delete release/v0.1.0

# Re-run the Release workflow
```

### Problem: No CI checks on release PR

**Symptom:** Release PR shows "0 checks" and no CI workflows run.

**Cause:** This is expected behavior. GitHub prevents workflows triggered by GITHUB_TOKEN from triggering other workflows (security feature).

**Solution:**
This is **not a problem** - it's by design. The Release Preparation workflow validates that CI passed on the current commit before creating the PR. Since the release PR only contains version/CHANGELOG updates (no code changes), re-running CI is unnecessary.

Simply review and merge the PR as usual.

### Problem: Tag already exists

**Symptom:**
```
Tag v0.1.0 already exists
```

**Cause:** Previous partial release created the tag.

**Solution:**
```bash
# Delete local tag
git tag -d v0.1.0

# Delete remote tag
git push origin --delete v0.1.0

# Re-run workflow
```

### Problem: Release Finalization doesn't trigger

**Symptom:** After merging release PR, the Release Finalization workflow doesn't run.

**Cause:** Release branch wasn't named correctly or PR wasn't merged (closed without merge).

**Solution:**
1. Check if PR was actually merged (not just closed):
   ```bash
   gh pr view <PR_NUMBER> --json merged
   ```

2. Verify branch name started with `release/`:
   ```bash
   gh pr view <PR_NUMBER> --json headRefName
   ```

3. If both are correct, manually trigger tag creation:
   ```bash
   git checkout main
   git pull origin main
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   git push origin vX.Y.Z
   gh release create vX.Y.Z --title "vX.Y.Z" --notes "See CHANGELOG.md"
   ```

### Problem: Forgot to approve release deployment

**Symptom:** Release Finalization workflow is waiting indefinitely for approval.

**Cause:** You haven't approved the deployment in GitHub Actions.

**Solution:**
1. Navigate to: [GitHub Actions](https://github.com/johnsosoka/jscom-python-common/actions)
2. Find the "Release Finalization" workflow run
3. Click "Review deployments"
4. Select the `release` environment
5. Click "Approve and deploy"

### Problem: Release Preparation workflow fails validation

**Symptom:** Release Preparation workflow fails during validation phase.

**Cause:** CI checks haven't passed on the current commit, tag already exists, or invalid version format.

**Solution:**
1. If CI checks haven't passed, fix the issues on main:
   ```bash
   git checkout main
   git pull

   # Run checks locally
   poetry run pre-commit run --all-files

   # Fix issues and commit
   git add .
   git commit -m "fix: resolve CI issues"
   git push origin main
   ```

2. Clean up failed release artifacts:
   ```bash
   # Close release PR if it exists
   gh pr close <PR_NUMBER>

   # Delete release branch
   git push origin --delete release/v0.1.0
   ```

3. Re-run release workflow

### Problem: Cleanup workflow doesn't run after failure

**Symptom:** Failed release leaves orphaned branches/PRs.

**Cause:** Cleanup workflow (`release-cleanup.yml`) may not have permissions or failed to detect the version.

**Manual Cleanup:**
```bash
# 1. Close any open release PRs
gh pr list --head release/v0.1.0
gh pr close <PR_NUMBER>

# 2. Delete release branch
git push origin --delete release/v0.1.0

# 3. Delete tag if it exists (and no release was created)
git ls-remote --tags origin v0.1.0
gh release view v0.1.0  # Check if release exists
# If release doesn't exist:
git push origin --delete v0.1.0
```

### Problem: Multiple release branches exist

**Symptom:** You see multiple `release/vX.Y.Z` branches in the repository.

**Cause:** Multiple failed release attempts or manual branch creation.

**Solution:**
```bash
# List all release branches
git branch -r | grep release/

# Delete each one
git push origin --delete release/v0.1.0
git push origin --delete release/v0.2.0
# ... etc
```

### Problem: Need to cancel an in-progress release

**Symptom:** Workflow is running but you need to stop it.

**Solution:**
```bash
# 1. Cancel the workflow run
gh run list --workflow=release.yml --limit 1
gh run cancel <RUN_ID>

# 2. Clean up any artifacts
gh pr list --head release/vX.Y.Z
gh pr close <PR_NUMBER> --comment "Cancelled release"

git push origin --delete release/vX.Y.Z
```

### Problem: Version mismatch after release

**Symptom:** Git tag exists but `pyproject.toml` version doesn't match.

**Cause:** Partial release completion or manual tag creation.

**Solution:**
```bash
# Check current versions
git describe --tags --abbrev=0  # Latest tag
grep version pyproject.toml     # pyproject.toml version

# If mismatch, decide:
# Option 1: Delete tag and re-release
git push origin --delete v0.1.0
# Then re-run workflow

# Option 2: Manually update pyproject.toml (not recommended)
poetry version 0.1.0
git add pyproject.toml
git commit -m "chore: sync version with tag"
git push origin main
```

### Getting Help

If you encounter issues not covered here:

1. **Check workflow logs:**
   - Navigate to GitHub Actions tab
   - Find the failed workflow run
   - Review step-by-step logs

2. **Check repository settings:**
   - Branch protection rules on `main`
   - Merge method settings (should allow squash)

3. **Open an issue:**
   - Include workflow run URL
   - Include error messages
   - Include steps to reproduce

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
