"""Tests for Cognito JWT validation utilities."""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from aws_lambda_powertools.event_handler.exceptions import UnauthorizedError

from jscom_common.auth.cognito import get_jwks, validate_jwt_token


class TestGetJWKS:
    """Tests for get_jwks function."""

    def test_get_jwks_success(self) -> None:
        """Test successful JWKS fetch and caching."""
        mock_jwks = {"keys": [{"kid": "test-key-id", "kty": "RSA", "n": "test-n", "e": "AQAB"}]}

        with patch("jscom_common.auth.cognito.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_jwks
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            # First call should fetch from Cognito
            result = get_jwks(region="us-west-2", user_pool_id="test-pool-id")
            assert result == mock_jwks
            assert mock_get.call_count == 1

            # Second call should use cache
            result2 = get_jwks(region="us-west-2", user_pool_id="test-pool-id")
            assert result2 == mock_jwks
            assert mock_get.call_count == 1  # Still 1, not 2

    def test_get_jwks_missing_user_pool_id(self) -> None:
        """Test that missing user pool ID raises ValueError."""
        with pytest.raises(ValueError, match="COGNITO_USER_POOL_ID"):
            get_jwks(region="us-west-2", user_pool_id=None)

    @patch.dict("os.environ", {"COGNITO_USER_POOL_ID": "env-pool-id"})
    def test_get_jwks_from_environment(self) -> None:
        """Test JWKS fetch using environment variables."""
        mock_jwks = {"keys": [{"kid": "test-key"}]}

        with patch("jscom_common.auth.cognito.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_jwks
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            result = get_jwks()
            assert result == mock_jwks


class TestValidateJWTToken:
    """Tests for validate_jwt_token function."""

    def test_missing_authorization_header(self) -> None:
        """Test that missing Authorization header raises UnauthorizedError."""
        event: dict[str, Any] = {"headers": {}}

        with pytest.raises(UnauthorizedError, match="Missing Authorization header"):
            validate_jwt_token(event)

    def test_invalid_authorization_header_format(self) -> None:
        """Test that invalid header format raises UnauthorizedError."""
        # Missing "Bearer" prefix
        event = {"headers": {"Authorization": "token123"}}

        with pytest.raises(UnauthorizedError, match="Invalid Authorization header format"):
            validate_jwt_token(event)

        # Empty bearer token
        event = {"headers": {"Authorization": "Bearer"}}

        with pytest.raises(UnauthorizedError, match="Invalid Authorization header format"):
            validate_jwt_token(event)

    @patch("jscom_common.auth.cognito.get_jwks")
    @patch("jscom_common.auth.cognito.jwt.get_unverified_header")
    @patch("jscom_common.auth.cognito.jwt.decode")
    def test_successful_token_validation(
        self,
        mock_decode: MagicMock,
        mock_get_header: MagicMock,
        mock_get_jwks: MagicMock,
    ) -> None:
        """Test successful JWT token validation."""
        event = {"headers": {"Authorization": "Bearer valid-token-123"}}

        mock_jwks = {"keys": [{"kid": "test-kid", "kty": "RSA", "n": "test-n", "e": "AQAB"}]}
        mock_get_jwks.return_value = mock_jwks

        mock_get_header.return_value = {"kid": "test-kid"}

        mock_claims = {"cognito:username": "testuser", "sub": "user-123", "email": "test@example.com"}
        mock_decode.return_value = mock_claims

        result = validate_jwt_token(event, region="us-west-2", user_pool_id="test-pool", app_client_id="test-client")

        assert result == mock_claims
        mock_decode.assert_called_once()

    @patch("jscom_common.auth.cognito.get_jwks")
    @patch("jscom_common.auth.cognito.jwt.get_unverified_header")
    def test_kid_not_found_in_jwks(
        self,
        mock_get_header: MagicMock,
        mock_get_jwks: MagicMock,
    ) -> None:
        """Test that missing key ID in JWKS raises UnauthorizedError."""
        event = {"headers": {"Authorization": "Bearer token123"}}

        mock_jwks = {"keys": [{"kid": "different-kid", "kty": "RSA"}]}
        mock_get_jwks.return_value = mock_jwks

        mock_get_header.return_value = {"kid": "test-kid"}

        with pytest.raises(UnauthorizedError, match="Invalid token"):
            validate_jwt_token(event, region="us-west-2", user_pool_id="test-pool", app_client_id="test-client")

    @patch("jscom_common.auth.cognito.get_jwks")
    @patch("jscom_common.auth.cognito.jwt.get_unverified_header")
    @patch("jscom_common.auth.cognito.jwt.decode")
    def test_jwt_decode_error(
        self,
        mock_decode: MagicMock,
        mock_get_header: MagicMock,
        mock_get_jwks: MagicMock,
    ) -> None:
        """Test that JWT decode error raises UnauthorizedError."""
        from jose import JWTError

        event = {"headers": {"Authorization": "Bearer invalid-token"}}

        mock_jwks = {"keys": [{"kid": "test-kid", "kty": "RSA"}]}
        mock_get_jwks.return_value = mock_jwks

        mock_get_header.return_value = {"kid": "test-kid"}

        mock_decode.side_effect = JWTError("Token expired")

        with pytest.raises(UnauthorizedError, match="Invalid or expired token"):
            validate_jwt_token(event, region="us-west-2", user_pool_id="test-pool", app_client_id="test-client")

    def test_case_insensitive_authorization_header(self) -> None:
        """Test that authorization header is case-insensitive."""
        # Lowercase "authorization"
        event_lower = {"headers": {"authorization": "invalid"}}

        with pytest.raises(UnauthorizedError):
            validate_jwt_token(event_lower, region="us-west-2", user_pool_id="test-pool", app_client_id="test-client")

        # Uppercase "Authorization"
        event_upper = {"headers": {"Authorization": "invalid"}}

        with pytest.raises(UnauthorizedError):
            validate_jwt_token(event_upper, region="us-west-2", user_pool_id="test-pool", app_client_id="test-client")

    def test_missing_required_parameters(self) -> None:
        """Test that missing required parameters raise ValueError."""
        event = {"headers": {"Authorization": "Bearer token123"}}

        with pytest.raises(ValueError, match="COGNITO_USER_POOL_ID"):
            validate_jwt_token(event, region="us-west-2", user_pool_id=None, app_client_id="test-client")

        with pytest.raises(ValueError, match="COGNITO_APP_CLIENT_ID"):
            validate_jwt_token(event, region="us-west-2", user_pool_id="test-pool", app_client_id=None)
