"""
Generic API response models for JSCOM services.

These models provide consistent structure for API responses across all JSCOM projects,
supporting both status-code-based and success-boolean-based patterns.
"""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """
    Generic API response wrapper providing consistent structure.

    This model supports two common patterns:
    1. Status-code pattern: status + data + error (contact-services, newsletter-services)
    2. Success-boolean pattern: success + data + error + message (homelab-services)

    Attributes:
        status: HTTP status code (optional, for status-code pattern)
        success: Success boolean (optional, for success-boolean pattern)
        data: Response payload (type varies by endpoint)
        error: Error message if request failed
        message: Additional informational message (optional)

    Examples:
        # Status-code pattern
        response = ApiResponse[User](status=200, data=user)

        # Success-boolean pattern
        response = ApiResponse[User](success=True, data=user, message="User retrieved")

        # Error response
        response = ApiResponse[None](status=404, error="User not found")
    """

    status: int | None = Field(default=None, description="HTTP status code")
    success: bool | None = Field(default=None, description="Whether the operation was successful")
    data: T | None = Field(default=None, description="Response data")
    error: str | None = Field(default=None, description="Error message")
    message: str | None = Field(default=None, description="Additional message")


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Paginated response for list endpoints with consistent structure.

    Supports pagination tokens for cursor-based pagination using DynamoDB LastEvaluatedKey.

    Attributes:
        items: List of items in the current page
        count: Number of items in current response
        next_token: Base64-encoded pagination token for next page (null if no more pages)

    Examples:
        # Return paginated list of users
        response = PaginatedResponse[User](
            items=[user1, user2],
            count=2,
            next_token="eyJpZCI6IjEyMyJ9"
        )

        # Last page (no more items)
        response = PaginatedResponse[User](
            items=[user1],
            count=1,
            next_token=None
        )
    """

    items: list[T] = Field(description="List of items")
    count: int = Field(description="Number of items in this page")
    next_token: str | None = Field(default=None, description="Token for next page (if available)")
