"""Error handler registration utility for FastAPI applications.

This module provides a centralized way to register all error handlers
with the FastAPI application instance, ensuring consistent error handling
across the entire application.
"""

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .error_handlers import (  # New standardized handlers; Legacy handlers (for backward compatibility)
    advisor360_exception_handler,
    domain_exception_handler,
    financial_year_not_found_handler,
    general_exception_handler,
    http_exception_handler,
    infrastructure_exception_handler,
    invalid_financial_year_handler,
    validation_exception_handler,
)
from .exceptions import (  # Domain exceptions; Infrastructure exceptions; Legacy exceptions
    Advisor360Exception,
    AuthorizationError,
    BusinessRuleViolation,
    CacheError,
    CommissionError,
    CommissionNotFound,
    ConfigurationError,
    ConnectionError,
    DatabaseError,
    DomainException,
    DuplicateError,
    ExternalServiceError,
    FileSystemError,
    FinancialYearError,
    FinancialYearNotFound,
    InfrastructureError,
    InvalidCommissionAmount,
    InvalidFinancialYearFormat,
    NotFoundError,
    PartnerError,
    PartnerHasCommissions,
    PartnerNotFound,
    SerializationError,
    SupabaseError,
    TimeoutError,
    TransactionError,
    TransactionNotFound,
    ValidationError,
)
from .middleware import ErrorHandlingMiddleware, RequestContextMiddleware


def register_error_handlers(app: FastAPI) -> None:
    """Register all error handlers with the FastAPI application.

    This function sets up comprehensive error handling by registering
    handlers for all exception types in the correct order of precedence.

    Args:
        app: FastAPI application instance
    """
    # Register middleware (order matters - they are applied in reverse order)
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(RequestContextMiddleware)

    # Register domain exception handlers (most specific first)

    # Specific domain exceptions
    app.add_exception_handler(ValidationError, domain_exception_handler)
    app.add_exception_handler(NotFoundError, domain_exception_handler)
    app.add_exception_handler(BusinessRuleViolation, domain_exception_handler)
    app.add_exception_handler(DuplicateError, domain_exception_handler)
    app.add_exception_handler(AuthorizationError, domain_exception_handler)
    app.add_exception_handler(ConfigurationError, domain_exception_handler)
    app.add_exception_handler(ExternalServiceError, domain_exception_handler)

    # Application-specific domain exceptions
    app.add_exception_handler(FinancialYearError, domain_exception_handler)
    app.add_exception_handler(PartnerError, domain_exception_handler)
    app.add_exception_handler(PartnerNotFound, domain_exception_handler)
    app.add_exception_handler(PartnerHasCommissions, domain_exception_handler)
    app.add_exception_handler(CommissionError, domain_exception_handler)
    app.add_exception_handler(CommissionNotFound, domain_exception_handler)
    app.add_exception_handler(InvalidCommissionAmount, domain_exception_handler)
    app.add_exception_handler(TransactionError, domain_exception_handler)
    app.add_exception_handler(TransactionNotFound, domain_exception_handler)

    # Base domain exception handler (catches all domain exceptions)
    app.add_exception_handler(DomainException, domain_exception_handler)

    # Register infrastructure exception handlers

    # Specific infrastructure exceptions
    app.add_exception_handler(DatabaseError, infrastructure_exception_handler)
    app.add_exception_handler(ConnectionError, infrastructure_exception_handler)
    app.add_exception_handler(TimeoutError, infrastructure_exception_handler)
    app.add_exception_handler(SupabaseError, infrastructure_exception_handler)
    app.add_exception_handler(CacheError, infrastructure_exception_handler)
    app.add_exception_handler(FileSystemError, infrastructure_exception_handler)
    app.add_exception_handler(SerializationError, infrastructure_exception_handler)

    # Base infrastructure exception handler
    app.add_exception_handler(InfrastructureError, infrastructure_exception_handler)

    # Register FastAPI built-in exception handlers
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)

    # Register legacy exception handlers (for backward compatibility)
    app.add_exception_handler(Advisor360Exception, advisor360_exception_handler)
    app.add_exception_handler(FinancialYearNotFound, financial_year_not_found_handler)
    app.add_exception_handler(
        InvalidFinancialYearFormat, invalid_financial_year_handler
    )

    # Register catch-all exception handler (must be last)
    app.add_exception_handler(Exception, general_exception_handler)


def setup_error_handling(app: FastAPI) -> None:
    """Complete error handling setup for the FastAPI application.

    This is the main function to call during application startup to
    configure all error handling components.

    Args:
        app: FastAPI application instance
    """
    register_error_handlers(app)

    # Log that error handling has been set up
    from .logging import error_logger

    error_logger.logger.info("Error handling system initialized successfully")


# Convenience function for backward compatibility
def setup_exception_handlers(app: FastAPI) -> None:
    """Legacy function name for backward compatibility.

    Args:
        app: FastAPI application instance
    """
    setup_error_handling(app)
