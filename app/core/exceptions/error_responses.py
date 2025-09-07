"""Standardized error response models for consistent API error handling.

This module defines the structure of error responses that will be returned
by the API to ensure consistency across all endpoints.
"""

import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Detailed error information for a specific error.

    This model provides structured information about individual errors,
    including field-specific validation errors.
    """

    field: Optional[str] = Field(None, description="The field that caused the error")
    message: str = Field(..., description="Human-readable error message")
    code: Optional[str] = Field(None, description="Machine-readable error code")
    value: Optional[str] = Field(
        None, description="The invalid value that caused the error"
    )


class ErrorResponse(BaseModel):
    """Standardized error response model.

    This model defines the structure of all error responses returned by the API
    to ensure consistency and provide comprehensive error information.
    """

    error: bool = Field(True, description="Always true for error responses")
    message: str = Field(..., description="Primary error message")
    error_code: str = Field(..., description="Machine-readable error code")
    error_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), description="Unique error identifier"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="When the error occurred"
    )

    # Optional fields for additional context
    details: Optional[list[ErrorDetail]] = Field(
        None, description="Detailed error information"
    )
    context: Optional[dict[str, Any]] = Field(
        None, description="Additional error context"
    )
    request_id: Optional[str] = Field(
        None, description="Request identifier for tracing"
    )

    # HTTP-specific fields
    status_code: Optional[int] = Field(None, description="HTTP status code")
    path: Optional[str] = Field(None, description="Request path that caused the error")
    method: Optional[str] = Field(None, description="HTTP method")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class ValidationErrorResponse(ErrorResponse):
    """Specialized error response for validation errors.

    This extends the base error response with validation-specific fields
    to provide detailed information about validation failures.
    """

    error_code: str = Field(
        "VALIDATION_ERROR", description="Always VALIDATION_ERROR for validation errors"
    )
    field_errors: Optional[dict[str, list[str]]] = Field(
        None, description="Field-specific error messages"
    )

    @classmethod
    def from_validation_errors(
        cls, errors: list[dict[str, Any]], message: str = "Validation failed", **kwargs
    ) -> "ValidationErrorResponse":
        """Create a validation error response from a list of validation errors.

        Args:
            errors: List of validation error dictionaries
            message: Primary error message
            **kwargs: Additional fields for the error response

        Returns:
            ValidationErrorResponse instance
        """
        details = []
        field_errors = {}

        for error in errors:
            field = error.get("loc", [])[-1] if error.get("loc") else None
            error_msg = error.get("msg", "Validation error")
            error_type = error.get("type", "validation_error")

            # Add to details
            details.append(
                ErrorDetail(
                    field=str(field) if field else None,
                    message=error_msg,
                    code=error_type,
                    value=(
                        str(error.get("input"))
                        if error.get("input") is not None
                        else None
                    ),
                )
            )

            # Add to field_errors
            if field:
                field_str = str(field)
                if field_str not in field_errors:
                    field_errors[field_str] = []
                field_errors[field_str].append(error_msg)

        return cls(
            message=message,
            details=details,
            field_errors=field_errors if field_errors else None,
            **kwargs,
        )


class NotFoundErrorResponse(ErrorResponse):
    """Specialized error response for not found errors.

    This extends the base error response with not-found-specific fields.
    """

    error_code: str = Field(
        "NOT_FOUND", description="Always NOT_FOUND for not found errors"
    )
    entity_type: Optional[str] = Field(
        None, description="Type of entity that was not found"
    )
    entity_id: Optional[str] = Field(
        None, description="ID of entity that was not found"
    )


class BusinessRuleErrorResponse(ErrorResponse):
    """Specialized error response for business rule violations.

    This extends the base error response with business-rule-specific fields.
    """

    error_code: str = Field(
        "BUSINESS_RULE_VIOLATION", description="Always BUSINESS_RULE_VIOLATION"
    )
    rule_name: Optional[str] = Field(
        None, description="Name of the violated business rule"
    )
    rule_description: Optional[str] = Field(
        None, description="Description of the business rule"
    )


class InternalServerErrorResponse(ErrorResponse):
    """Specialized error response for internal server errors.

    This extends the base error response for 5xx errors while hiding
    sensitive internal details from the client.
    """

    error_code: str = Field(
        "INTERNAL_SERVER_ERROR", description="Always INTERNAL_SERVER_ERROR"
    )
    message: str = Field(
        "An internal server error occurred", description="Generic error message"
    )

    # Override sensitive fields to not expose internal details
    context: Optional[dict[str, Any]] = Field(
        None, description="Limited context for security"
    )


def create_error_response(
    exception: Exception,
    status_code: int,
    request_path: Optional[str] = None,
    request_method: Optional[str] = None,
    request_id: Optional[str] = None,
) -> ErrorResponse:
    """Create an appropriate error response based on the exception type.

    Args:
        exception: The exception that occurred
        status_code: HTTP status code
        request_path: Request path that caused the error
        request_method: HTTP method
        request_id: Request identifier for tracing

    Returns:
        Appropriate ErrorResponse subclass instance
    """
    from .domain_exceptions import (
        BusinessRuleViolation,
        DomainException,
        NotFoundError,
        ValidationError,
    )

    base_kwargs = {
        "status_code": status_code,
        "path": request_path,
        "method": request_method,
        "request_id": request_id,
    }

    if isinstance(exception, ValidationError):
        return ValidationErrorResponse(
            message=exception.message,
            error_code=exception.error_code,
            error_id=getattr(exception, "error_id", str(uuid.uuid4())),
            timestamp=getattr(exception, "timestamp", datetime.utcnow()),
            context=getattr(exception, "context", None),
            details=(
                [
                    ErrorDetail(
                        field=exception.field,
                        message=exception.message,
                        code=exception.error_code,
                        value=(
                            str(exception.value)
                            if exception.value is not None
                            else None
                        ),
                    )
                ]
                if exception.field
                else None
            ),
            **base_kwargs,
        )

    elif isinstance(exception, NotFoundError):
        return NotFoundErrorResponse(
            message=exception.message,
            error_code=exception.error_code,
            error_id=getattr(exception, "error_id", str(uuid.uuid4())),
            timestamp=getattr(exception, "timestamp", datetime.utcnow()),
            context=getattr(exception, "context", None),
            entity_type=exception.entity_type,
            entity_id=exception.entity_id,
            **base_kwargs,
        )

    elif isinstance(exception, BusinessRuleViolation):
        return BusinessRuleErrorResponse(
            message=exception.message,
            error_code=exception.error_code,
            error_id=getattr(exception, "error_id", str(uuid.uuid4())),
            timestamp=getattr(exception, "timestamp", datetime.utcnow()),
            context=getattr(exception, "context", None),
            rule_name=exception.rule_name,
            **base_kwargs,
        )

    elif isinstance(exception, DomainException):
        return ErrorResponse(
            message=exception.message,
            error_code=exception.error_code,
            error_id=exception.error_id,
            timestamp=exception.timestamp,
            context=exception.context,
            **base_kwargs,
        )

    else:
        # For non-domain exceptions, create a generic error response
        if status_code >= 500:
            return InternalServerErrorResponse(
                error_id=str(uuid.uuid4()), **base_kwargs
            )
        else:
            return ErrorResponse(
                message=str(exception),
                error_code=exception.__class__.__name__,
                **base_kwargs,
            )
