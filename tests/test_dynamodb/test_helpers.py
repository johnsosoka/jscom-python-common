"""Tests for DynamoDB helper utilities."""

import base64
import json

import pytest
from pydantic import BaseModel, ValidationError

from jscom_common.dynamodb.helpers import (
    decode_pagination_token,
    dynamodb_to_pydantic,
    encode_pagination_token,
    pydantic_to_dynamodb,
)


class SampleModel(BaseModel):
    """Sample Pydantic model for testing."""

    id: str
    name: str
    email: str | None = None
    age: int | None = None


class TestPaginationTokens:
    """Tests for pagination token encoding/decoding."""

    def test_encode_pagination_token(self) -> None:
        """Test encoding DynamoDB LastEvaluatedKey to base64 token."""
        last_key = {"id": "123", "timestamp": 1234567890}
        token = encode_pagination_token(last_key)

        # Token should be base64 encoded
        assert isinstance(token, str)
        assert len(token) > 0

        # Should be decodable
        decoded = base64.b64decode(token.encode("utf-8"))
        decoded_data = json.loads(decoded.decode("utf-8"))
        assert decoded_data == last_key

    def test_decode_pagination_token(self) -> None:
        """Test decoding base64 token to DynamoDB ExclusiveStartKey."""
        last_key = {"id": "456", "sort_key": "abc"}
        token = encode_pagination_token(last_key)

        decoded_key = decode_pagination_token(token)
        assert decoded_key == last_key

    def test_decode_invalid_token(self) -> None:
        """Test decoding invalid pagination token raises ValueError."""
        with pytest.raises(ValueError, match="Invalid pagination token"):
            decode_pagination_token("invalid-token-!!!!")

    def test_encode_decode_roundtrip(self) -> None:
        """Test encoding and decoding roundtrip preserves data."""
        original = {"id": "789", "timestamp": 1111111111, "status": "active"}
        token = encode_pagination_token(original)
        decoded = decode_pagination_token(token)

        assert decoded == original

    def test_encode_empty_dict(self) -> None:
        """Test encoding empty dictionary."""
        token = encode_pagination_token({})
        decoded = decode_pagination_token(token)
        assert decoded == {}


class TestPydanticToDynamoDB:
    """Tests for Pydantic model to DynamoDB item conversion."""

    def test_pydantic_to_dynamodb_all_fields(self) -> None:
        """Test converting Pydantic model with all fields to DynamoDB item."""
        model = SampleModel(id="123", name="John", email="john@example.com", age=30)
        item = pydantic_to_dynamodb(model)

        assert item == {"id": "123", "name": "John", "email": "john@example.com", "age": 30}

    def test_pydantic_to_dynamodb_excludes_none(self) -> None:
        """Test that None values are excluded from DynamoDB item."""
        model = SampleModel(id="456", name="Jane", email=None, age=None)
        item = pydantic_to_dynamodb(model)

        assert item == {"id": "456", "name": "Jane"}
        assert "email" not in item
        assert "age" not in item

    def test_pydantic_to_dynamodb_partial_none(self) -> None:
        """Test conversion with some None values."""
        model = SampleModel(id="789", name="Bob", email="bob@example.com", age=None)
        item = pydantic_to_dynamodb(model)

        assert item == {"id": "789", "name": "Bob", "email": "bob@example.com"}
        assert "age" not in item


class TestDynamoDBToPydantic:
    """Tests for DynamoDB item to Pydantic model conversion."""

    def test_dynamodb_to_pydantic_all_fields(self) -> None:
        """Test converting DynamoDB item to Pydantic model with all fields."""
        item = {"id": "123", "name": "John", "email": "john@example.com", "age": 30}
        model = dynamodb_to_pydantic(item, SampleModel)

        assert model.id == "123"
        assert model.name == "John"
        assert model.email == "john@example.com"
        assert model.age == 30

    def test_dynamodb_to_pydantic_optional_fields(self) -> None:
        """Test conversion with optional fields missing."""
        item = {"id": "456", "name": "Jane"}
        model = dynamodb_to_pydantic(item, SampleModel)

        assert model.id == "456"
        assert model.name == "Jane"
        assert model.email is None
        assert model.age is None

    def test_dynamodb_to_pydantic_validation_error(self) -> None:
        """Test that invalid data raises ValidationError."""
        item = {"id": "789"}  # Missing required 'name' field

        with pytest.raises(ValidationError):
            dynamodb_to_pydantic(item, SampleModel)

    def test_dynamodb_to_pydantic_wrong_type(self) -> None:
        """Test that wrong field types raise ValidationError."""
        item = {"id": "123", "name": "John", "age": "not-an-integer"}

        with pytest.raises(ValidationError):
            dynamodb_to_pydantic(item, SampleModel)


class TestRoundtripConversion:
    """Tests for roundtrip conversions between Pydantic and DynamoDB."""

    def test_roundtrip_with_all_fields(self) -> None:
        """Test roundtrip conversion preserves all data."""
        original = SampleModel(id="123", name="John", email="john@example.com", age=30)
        item = pydantic_to_dynamodb(original)
        restored = dynamodb_to_pydantic(item, SampleModel)

        assert restored == original

    def test_roundtrip_with_none_fields(self) -> None:
        """Test roundtrip conversion with None fields."""
        original = SampleModel(id="456", name="Jane", email=None, age=None)
        item = pydantic_to_dynamodb(original)
        restored = dynamodb_to_pydantic(item, SampleModel)

        assert restored == original
        assert restored.email is None
        assert restored.age is None
