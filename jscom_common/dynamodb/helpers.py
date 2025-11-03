"""
DynamoDB helper utilities for JSCOM services.

Provides utilities for pagination token encoding/decoding and Pydantic model conversions
for working with DynamoDB items.

Module Organization Note:
    This module currently combines pagination and Pydantic utilities (~120 lines).
    Consider splitting into separate modules when file exceeds ~300 lines:
    - dynamodb/pagination.py (encode/decode tokens, query helpers)
    - dynamodb/pydantic.py (model conversion utilities)
    - dynamodb/batch.py (batch operations, transact writes)
    - dynamodb/streams.py (DynamoDB streams processing)
"""

import base64
import json
from typing import Any, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def encode_pagination_token(last_key: dict[str, Any]) -> str:
    """
    Encode DynamoDB LastEvaluatedKey as base64 pagination token.

    Args:
        last_key: LastEvaluatedKey dictionary from DynamoDB query or scan response

    Returns:
        Base64-encoded token string

    Examples:
        >>> last_key = {"id": "123", "timestamp": 1234567890}
        >>> token = encode_pagination_token(last_key)
        >>> print(token)
        'eyJpZCI6ICIxMjMiLCAidGltZXN0YW1wIjogMTIzNDU2Nzg5MH0='
    """
    json_str = json.dumps(last_key)
    encoded = base64.b64encode(json_str.encode("utf-8"))
    return encoded.decode("utf-8")


def decode_pagination_token(token: str) -> dict[str, Any]:
    """
    Decode base64 pagination token to DynamoDB ExclusiveStartKey.

    Args:
        token: Base64-encoded pagination token from previous response

    Returns:
        DynamoDB ExclusiveStartKey dictionary

    Raises:
        ValueError: If token is invalid or malformed

    Examples:
        >>> token = "eyJpZCI6ICIxMjMifQ=="
        >>> start_key = decode_pagination_token(token)
        >>> print(start_key)
        {'id': '123'}
    """
    try:
        decoded = base64.b64decode(token.encode("utf-8"))
        result: dict[str, Any] = json.loads(decoded.decode("utf-8"))
        return result
    except Exception as e:
        raise ValueError(f"Invalid pagination token: {e}")


def pydantic_to_dynamodb(model: BaseModel) -> dict[str, Any]:
    """
    Convert Pydantic model to DynamoDB item dictionary.

    Removes None values which DynamoDB doesn't support, and converts the model
    to a dictionary using Pydantic's model_dump().

    Args:
        model: Pydantic model instance

    Returns:
        DynamoDB-compatible dictionary with None values excluded

    Examples:
        >>> from pydantic import BaseModel
        >>> class User(BaseModel):
        ...     id: str
        ...     name: str
        ...     email: str | None = None
        >>> user = User(id="123", name="John", email=None)
        >>> item = pydantic_to_dynamodb(user)
        >>> print(item)
        {'id': '123', 'name': 'John'}
    """
    return model.model_dump(exclude_none=True)


def dynamodb_to_pydantic(item: dict[str, Any], model_class: type[T]) -> T:
    """
    Convert DynamoDB item to Pydantic model instance.

    Uses Pydantic's model_validate() to create a type-safe model instance from
    DynamoDB item dictionary. Boto3 resource API returns native Python types,
    so minimal transformation is needed.

    Args:
        item: DynamoDB item dictionary (from boto3 resource API)
        model_class: Pydantic model class to instantiate

    Returns:
        Validated Pydantic model instance

    Raises:
        ValidationError: If item doesn't match model schema

    Examples:
        >>> from pydantic import BaseModel
        >>> class User(BaseModel):
        ...     id: str
        ...     name: str
        ...     email: str
        >>> item = {"id": "123", "name": "John", "email": "john@example.com"}
        >>> user = dynamodb_to_pydantic(item, User)
        >>> print(user.name)
        'John'
    """
    return model_class.model_validate(item)
