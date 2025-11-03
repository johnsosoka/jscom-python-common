"""AWS Cognito JWT token validation utilities for JSCOM services."""

import os
from typing import Any

import requests
from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler.exceptions import UnauthorizedError
from jose import JWTError, jwt

# Initialize logger
logger = Logger(child=True)

# Cache for JWKS (JSON Web Key Set)
_jwks_cache: dict[str, Any] | None = None


def get_jwks(
    region: str | None = None,
    user_pool_id: str | None = None,
) -> dict[str, Any]:
    """
    Fetch and cache the JWKS from Cognito.

    Args:
        region: AWS region for Cognito (defaults to COGNITO_REGION env var or us-west-2)
        user_pool_id: Cognito User Pool ID (defaults to COGNITO_USER_POOL_ID env var)

    Returns:
        JWKS dictionary from Cognito

    Raises:
        requests.RequestException: If JWKS fetch fails
    """
    global _jwks_cache

    if _jwks_cache is None:
        cognito_region = region or os.environ.get("COGNITO_REGION", "us-west-2")
        cognito_user_pool_id = user_pool_id or os.environ.get("COGNITO_USER_POOL_ID", "")

        if not cognito_user_pool_id:
            raise ValueError("COGNITO_USER_POOL_ID environment variable or user_pool_id parameter is required")

        jwks_url = f"https://cognito-idp.{cognito_region}.amazonaws.com/{cognito_user_pool_id}/.well-known/jwks.json"
        logger.info(f"Fetching JWKS from {jwks_url}")
        response = requests.get(jwks_url, timeout=10)
        response.raise_for_status()
        _jwks_cache = response.json()

    return _jwks_cache


def validate_jwt_token(
    event: dict[str, Any],
    region: str | None = None,
    user_pool_id: str | None = None,
    app_client_id: str | None = None,
) -> dict[str, Any]:
    """
    Validate JWT token from Authorization header in API Gateway event.

    Args:
        event: API Gateway event containing headers
        region: AWS region for Cognito (defaults to COGNITO_REGION env var or us-west-2)
        user_pool_id: Cognito User Pool ID (defaults to COGNITO_USER_POOL_ID env var)
        app_client_id: Cognito App Client ID (defaults to COGNITO_APP_CLIENT_ID env var)

    Returns:
        Decoded JWT claims if valid

    Raises:
        UnauthorizedError: If token is missing, invalid, or expired
    """
    # Get Authorization header
    headers = event.get("headers", {})
    auth_header = headers.get("authorization") or headers.get("Authorization")

    if not auth_header:
        logger.warning("Missing Authorization header")
        raise UnauthorizedError("Missing Authorization header")

    # Extract token from "Bearer <token>"
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        logger.warning("Invalid Authorization header format")
        raise UnauthorizedError("Invalid Authorization header format")

    token = parts[1]

    # Get configuration from environment or parameters
    cognito_region = region or os.environ.get("COGNITO_REGION", "us-west-2")
    cognito_user_pool_id = user_pool_id or os.environ.get("COGNITO_USER_POOL_ID", "")
    cognito_app_client_id = app_client_id or os.environ.get("COGNITO_APP_CLIENT_ID", "")

    if not cognito_user_pool_id:
        raise ValueError("COGNITO_USER_POOL_ID environment variable or user_pool_id parameter is required")
    if not cognito_app_client_id:
        raise ValueError("COGNITO_APP_CLIENT_ID environment variable or app_client_id parameter is required")

    try:
        # Get JWKS
        jwks = get_jwks(region=cognito_region, user_pool_id=cognito_user_pool_id)

        # Decode token header to get key ID
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        # Find the matching key
        key = None
        for jwk_key in jwks["keys"]:
            if jwk_key["kid"] == kid:
                key = jwk_key
                break

        if not key:
            logger.warning(f"Public key not found for kid: {kid}")
            raise UnauthorizedError("Invalid token")

        # Verify and decode the token
        claims_result: dict[str, Any] = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=cognito_app_client_id,
            issuer=f"https://cognito-idp.{cognito_region}.amazonaws.com/{cognito_user_pool_id}",
        )

        logger.info(f"Token validated for user: {claims_result.get('cognito:username')}")
        return claims_result

    except UnauthorizedError:
        # Re-raise UnauthorizedError without modification
        raise
    except JWTError as e:
        logger.warning(f"JWT validation failed: {e}")
        raise UnauthorizedError("Invalid or expired token")
    except Exception as e:
        logger.exception(f"Unexpected error during token validation: {e}")
        raise UnauthorizedError("Token validation failed")
