"""Common DTOs used across all API endpoints."""

from datetime import datetime
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class BaseResponse(BaseModel):
    """Base response model for all API responses."""

    success: bool = Field(True, description="Indicates if the request was successful")
    message: str = Field(..., description="Human-readable message")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Response timestamp"
    )


class SuccessResponse(BaseResponse):
    """Simple success response without data."""

    pass


class ErrorDetail(BaseModel):
    """Detailed error information."""

    field: Optional[str] = Field(None, description="Field that caused the error")
    message: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")


class ErrorResponse(BaseModel):
    """Standard error response model."""

    success: bool = Field(False, description="Always false for errors")
    message: str = Field(..., description="Error message")
    details: Optional[list[ErrorDetail]] = Field(
        None, description="Detailed error information"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Error timestamp"
    )
    request_id: Optional[str] = Field(None, description="Request ID for tracking")


class PaginationMeta(BaseModel):
    """Pagination metadata."""

    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    total: int = Field(..., description="Total number of items")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")


class PaginatedResponse(BaseResponse, Generic[T]):
    """Paginated response model."""

    data: list[T] = Field(..., description="List of items")
    meta: PaginationMeta = Field(..., description="Pagination metadata")


class DataResponse(BaseResponse, Generic[T]):
    """Response model with data payload."""

    data: T = Field(..., description="Response data")


class ListResponse(BaseResponse, Generic[T]):
    """Response model for list endpoints."""

    data: list[T] = Field(..., description="List of items")
    count: int = Field(..., description="Number of items returned")


class ValidationError(BaseModel):
    """Validation error details."""

    field: str = Field(..., description="Field name")
    message: str = Field(..., description="Validation error message")
    value: Any = Field(None, description="Invalid value")


class HealthCheckResponse(BaseModel):
    """Health check response model."""

    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Check timestamp"
    )
    version: Optional[str] = Field(None, description="Application version")
    database_status: Optional[str] = Field(
        None, description="Database connection status"
    )
    dependencies: Optional[dict[str, str]] = Field(
        None, description="Status of external dependencies"
    )
