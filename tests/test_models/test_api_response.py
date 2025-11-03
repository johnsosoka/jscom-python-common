"""Tests for API response models."""

import pytest
from pydantic import BaseModel

from jscom_common.models import ApiResponse, PaginatedResponse


class SampleData(BaseModel):
    """Sample data model for testing."""

    id: str
    name: str
    email: str


class TestApiResponse:
    """Tests for ApiResponse model."""

    def test_status_code_pattern(self) -> None:
        """Test status-code pattern with data."""
        data = SampleData(id="123", name="John", email="john@example.com")
        response = ApiResponse[SampleData](status=200, data=data)

        assert response.status == 200
        assert response.data == data
        assert response.error is None
        assert response.success is None
        assert response.message is None

    def test_status_code_pattern_with_error(self) -> None:
        """Test status-code pattern with error."""
        response = ApiResponse[None](status=404, error="Not found")

        assert response.status == 404
        assert response.data is None
        assert response.error == "Not found"

    def test_success_boolean_pattern(self) -> None:
        """Test success-boolean pattern with data."""
        data = SampleData(id="456", name="Jane", email="jane@example.com")
        response = ApiResponse[SampleData](success=True, data=data, message="User retrieved")

        assert response.success is True
        assert response.data == data
        assert response.message == "User retrieved"
        assert response.error is None
        assert response.status is None

    def test_success_boolean_pattern_with_error(self) -> None:
        """Test success-boolean pattern with error."""
        response = ApiResponse[None](success=False, error="Operation failed", message="Invalid input")

        assert response.success is False
        assert response.data is None
        assert response.error == "Operation failed"
        assert response.message == "Invalid input"

    def test_serialization(self) -> None:
        """Test model serialization to dict."""
        data = SampleData(id="789", name="Bob", email="bob@example.com")
        response = ApiResponse[SampleData](status=200, data=data)

        serialized = response.model_dump()
        assert serialized["status"] == 200
        assert serialized["data"]["id"] == "789"
        assert serialized["error"] is None


class TestPaginatedResponse:
    """Tests for PaginatedResponse model."""

    def test_paginated_response_with_next_token(self) -> None:
        """Test paginated response with next token."""
        items = [
            SampleData(id="1", name="User 1", email="user1@example.com"),
            SampleData(id="2", name="User 2", email="user2@example.com"),
        ]
        response = PaginatedResponse[SampleData](items=items, count=2, next_token="abc123")

        assert response.items == items
        assert response.count == 2
        assert response.next_token == "abc123"

    def test_paginated_response_last_page(self) -> None:
        """Test paginated response on last page (no next token)."""
        items = [
            SampleData(id="3", name="User 3", email="user3@example.com"),
        ]
        response = PaginatedResponse[SampleData](items=items, count=1, next_token=None)

        assert response.items == items
        assert response.count == 1
        assert response.next_token is None

    def test_paginated_response_empty(self) -> None:
        """Test paginated response with no items."""
        response = PaginatedResponse[SampleData](items=[], count=0, next_token=None)

        assert response.items == []
        assert response.count == 0
        assert response.next_token is None

    def test_serialization(self) -> None:
        """Test model serialization to dict."""
        items = [SampleData(id="4", name="User 4", email="user4@example.com")]
        response = PaginatedResponse[SampleData](items=items, count=1, next_token="xyz")

        serialized = response.model_dump()
        assert serialized["count"] == 1
        assert len(serialized["items"]) == 1
        assert serialized["next_token"] == "xyz"
