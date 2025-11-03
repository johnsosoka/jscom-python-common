"""Pytest configuration and shared fixtures."""

import pytest


@pytest.fixture(autouse=True)
def reset_jwks_cache() -> None:
    """Reset the JWKS cache before each test to ensure test isolation."""
    import jscom_common.auth.cognito as cognito_module

    cognito_module._jwks_cache = None
