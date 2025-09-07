"""Comprehensive error handlers for FastAPI application with standardized responses.

This module provides global error handlers that catch exceptions throughout
the application and return consistent, structured error responses while
ensuring proper logging and context preservation.
"""

import uuid
from typing import Union

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .exceptions import (  # Domain exceptions; Infrastructure exceptions
    AuthorizationError,
    BusinessRuleViolation,
    CommissionNotFound,
    ConnectionError,
    DatabaseError,
    DomainException,
    DuplicateError,
    FinancialYearError,
    InfrastructureError,
    NotFoundError,
    PartnerNotFound,
    TimeoutError,
    ValidationError,
)
from .exceptions.error_responses import (
    ErrorResponse,
    InternalServerErrorResponse,
    ValidationErrorResponse,
    create_error_response,
)
from .logging.error_logger import error_context, error_logger


def get_request_id(request: Request) -> str:
    """Extract or generate request ID for tracing."""
    return getattr(request.state, "request_id", str(uuid.uuid4()))


def get_user_id(request: Request) -> str:
    """Extract user ID from request if available."""
    return getattr(request.state, "user_id", None)


async def domain_exception_handler(
    request: Request, exc: DomainException
) -> JSONResponse:
    """Handle domain exceptions with structured logging and responses.

    Args:
        request: FastAPI request object
        exc: Domain exception that occurred

    Returns:
        JSONResponse with structured error data
    """
    request_id = get_request_id(request)
    user_id = get_user_id(request)

    with error_context(request_id=request_id, user_id=user_id):
        # Log the error with appropriate severity
        if isinstance(exc, (ValidationError, NotFoundError)):
            error_logger.log_error(exc, severity="WARNING")
            status_code = 400 if isinstance(exc, ValidationError) else 404
        elif isinstance(exc, BusinessRuleViolation):
            error_logger.log_business_rule_violation(
                exc,
                exc.rule_name,
                exc.context.get("entity_type"),
                exc.context.get("entity_id"),
            )
            status_code = 422
        elif isinstance(exc, AuthorizationError):
            error_logger.log_error(exc, severity="WARNING")
            status_code = 403
        elif isinstance(exc, DuplicateError):
            error_logger.log_error(exc, severity="WARNING")
            status_code = 409
        else:
            error_logger.log_error(exc, severity="ERROR")
            status_code = 400

    # Create structured error response
    error_response = create_error_response(
        exc,
        status_code,
        request_path=str(request.url.path),
        request_method=request.method,
        request_id=request_id,
    )

    return JSONResponse(status_code=status_code, content=error_response.dict())


async def infrastructure_exception_handler(
    request: Request, exc: InfrastructureError
) -> JSONResponse:
    """Handle infrastructure exceptions with proper logging and generic responses.

    Args:
        request: FastAPI request object
        exc: Infrastructure exception that occurred

    Returns:
        JSONResponse with generic error message (hiding internal details)
    """
    request_id = get_request_id(request)
    user_id = get_user_id(request)

    with error_context(request_id=request_id, user_id=user_id):
        # Log infrastructure errors with full context
        if isinstance(exc, (ConnectionError, TimeoutError)):
            error_logger.log_infrastructure_error(
                exc,
                service=getattr(exc, "service", "unknown"),
                operation=getattr(exc, "operation", "unknown"),
            )
            status_code = 503  # Service Unavailable
        elif isinstance(exc, DatabaseError):
            error_logger.log_infrastructure_error(
                exc, service="database", operation=getattr(exc, "operation", "unknown")
            )
            status_code = 500
        else:
            error_logger.log_error(exc, severity="ERROR")
            status_code = 500

    # Return generic error response to avoid exposing internal details
    error_response = InternalServerErrorResponse(
        error_id=str(uuid.uuid4()),
        status_code=status_code,
        path=str(request.url.path),
        method=request.method,
        request_id=request_id,
    )

    return JSONResponse(status_code=status_code, content=error_response.dict())


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle FastAPI validation errors with structured responses.

    Args:
        request: FastAPI request object
        exc: Request validation error

    Returns:
        JSONResponse with detailed validation error information
    """
    request_id = get_request_id(request)
    user_id = get_user_id(request)

    with error_context(request_id=request_id, user_id=user_id):
        error_logger.log_validation_error(exc)

    # Create structured validation error response
    error_response = ValidationErrorResponse.from_validation_errors(
        exc.errors(),
        message="Request validation failed",
        status_code=422,
        path=str(request.url.path),
        method=request.method,
        request_id=request_id,
    )

    return JSONResponse(status_code=422, content=error_response.dict())


async def http_exception_handler(
    request: Request, exc: Union[HTTPException, StarletteHTTPException]
) -> JSONResponse:
    """Handle HTTP exceptions with consistent response format.

    Args:
        request: FastAPI request object
        exc: HTTP exception

    Returns:
        JSONResponse with structured error data
    """
    request_id = get_request_id(request)
    user_id = get_user_id(request)

    with error_context(request_id=request_id, user_id=user_id):
        if exc.status_code >= 500:
            error_logger.log_error(exc, severity="ERROR")
        else:
            error_logger.log_error(exc, severity="WARNING")

    error_response = ErrorResponse(
        message=exc.detail if hasattr(exc, "detail") else str(exc),
        error_code=f"HTTP_{exc.status_code}",
        status_code=exc.status_code,
        path=str(request.url.path),
        method=request.method,
        request_id=request_id,
    )

    return JSONResponse(status_code=exc.status_code, content=error_response.dict())


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions with proper logging and generic responses.

    Args:
        request: FastAPI request object
        exc: Unexpected exception

    Returns:
        JSONResponse with generic error message
    """
    request_id = get_request_id(request)
    user_id = get_user_id(request)

    with error_context(request_id=request_id, user_id=user_id):
        error_logger.log_critical_error(
            exc,
            system_impact="Unexpected error in request processing",
            recovery_action="Check logs and investigate root cause",
        )

    # Return generic error response for security
    error_response = InternalServerErrorResponse(
        error_id=str(uuid.uuid4()),
        status_code=500,
        path=str(request.url.path),
        method=request.method,
        request_id=request_id,
    )

    return JSONResponse(status_code=500, content=error_response.dict())


# Legacy exception handlers for backward compatibility


async def advisor360_exception_handler(
    request: Request, exc: DomainException
) -> JSONResponse:
    """Handle legacy Advisor360 exceptions (backward compatibility)."""
    return await domain_exception_handler(request, exc)


async def financial_year_not_found_handler(
    request: Request, exc: FinancialYearError
) -> JSONResponse:
    """Handle legacy financial year not found exceptions (backward compatibility)."""
    return await domain_exception_handler(request, exc)


async def partner_not_found_handler(
    request: Request, exc: PartnerNotFound
) -> JSONResponse:
    """Handle legacy partner not found exceptions (backward compatibility)."""
    return await domain_exception_handler(request, exc)


async def commission_not_found_handler(
    request: Request, exc: CommissionNotFound
) -> JSONResponse:
    """Handle legacy commission not found exceptions (backward compatibility)."""
    return await domain_exception_handler(request, exc)


async def invalid_financial_year_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    """Handle legacy invalid financial year format exceptions (backward compatibility)."""
    return await domain_exception_handler(request, exc)


async def database_error_handler(request: Request, exc: DatabaseError) -> JSONResponse:
    """Handle legacy database error exceptions (backward compatibility)."""
    return await infrastructure_exception_handler(request, exc)
