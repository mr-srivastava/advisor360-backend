# Standardized Error Handling System

This directory contains a comprehensive error handling system that provides consistent error management, structured logging, and standardized API responses across the entire application.

## Overview

The error handling system is built around three core principles:

1. **Structured Exception Hierarchy**: Domain-specific exceptions that carry context and metadata
2. **Comprehensive Logging**: Structured logging with request tracing and severity management
3. **Consistent API Responses**: Standardized error response formats for all API endpoints

## Components

### Exception Hierarchy

#### Domain Exceptions (`domain_exceptions.py`)

Base exceptions for business logic and domain-specific errors:

- `DomainException`: Base class for all domain exceptions
- `ValidationError`: Data validation failures
- `NotFoundError`: Entity not found errors
- `BusinessRuleViolation`: Business rule violations
- `DuplicateError`: Duplicate entity creation attempts
- `AuthorizationError`: Access control violations
- `ConfigurationError`: Configuration issues

Application-specific exceptions:

- `PartnerNotFound`, `CommissionNotFound`, `TransactionNotFound`
- `InvalidCommissionAmount`, `FinancialYearError`
- `PartnerHasCommissions` (business rule violation)

#### Infrastructure Exceptions (`infrastructure_exceptions.py`)

Exceptions for technical and infrastructure concerns:

- `InfrastructureError`: Base class for infrastructure exceptions
- `DatabaseError`: Database operation failures
- `ConnectionError`: Service connection issues
- `TimeoutError`: Operation timeout failures
- `SupabaseError`: Supabase-specific errors
- `CacheError`: Caching operation failures
- `FileSystemError`: File I/O errors
- `SerializationError`: Data serialization issues

### Error Responses (`error_responses.py`)

Standardized response models for consistent API error responses:

- `ErrorResponse`: Base error response structure
- `ValidationErrorResponse`: Detailed validation error information
- `NotFoundErrorResponse`: Entity not found responses
- `BusinessRuleErrorResponse`: Business rule violation responses
- `InternalServerErrorResponse`: Generic server error responses

### Logging System (`../logging/error_logger.py`)

Structured error logging with context management:

- `StructuredErrorLogger`: Main logging class with context support
- `error_context`: Context manager for request tracing
- Severity-based logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Request ID and correlation ID tracking

### Error Handlers (`../error_handlers.py`)

Global FastAPI exception handlers:

- `domain_exception_handler`: Handles all domain exceptions
- `infrastructure_exception_handler`: Handles infrastructure exceptions
- `validation_exception_handler`: Handles FastAPI validation errors
- `http_exception_handler`: Handles HTTP exceptions
- `general_exception_handler`: Catch-all for unexpected exceptions

### Middleware (`../middleware/error_middleware.py`)

Request-level error handling and context management:

- `ErrorHandlingMiddleware`: Catches unhandled exceptions
- `RequestContextMiddleware`: Sets up request context and tracing

## Usage

### 1. Raising Domain Exceptions

```python
from app.core.exceptions import ValidationError, PartnerNotFound, BusinessRuleViolation

# Validation error
if not partner_id:
    raise ValidationError(
        "Partner ID is required",
        field="partner_id",
        validation_rule="required"
    )

# Not found error
if not partner:
    raise PartnerNotFound(partner_id)

# Business rule violation
if partner.commission_count > 0:
    raise BusinessRuleViolation(
        rule_name="partner_has_commissions",
        message="Cannot delete partner with existing commissions",
        context={"partner_id": partner_id, "commission_count": partner.commission_count}
    )
```

### 2. Raising Infrastructure Exceptions

```python
from app.core.exceptions import DatabaseError, SupabaseError, ConnectionError

# Database error
try:
    result = await supabase.table("partners").select("*").execute()
except Exception as e:
    raise DatabaseError(
        operation="select_partners",
        table="partners",
        original_error=e
    )

# Connection error
if not connection.is_connected():
    raise ConnectionError(
        service="supabase",
        host="your-project.supabase.co"
    )
```

### 3. Using Error Logging

```python
from app.core.logging import error_logger, error_context, log_exception

# Basic error logging
try:
    risky_operation()
except Exception as e:
    error_logger.log_error(e, severity="ERROR")
    raise

# With request context
with error_context(request_id="req_123", user_id="user_456"):
    try:
        process_request()
    except ValidationError as e:
        error_logger.log_validation_error(e, field=e.field, value=e.value)
        raise

# Convenience function
try:
    critical_operation()
except Exception as e:
    log_exception(e, severity="CRITICAL", context={"operation": "critical_op"})
    raise
```

### 4. Setting Up Error Handling in FastAPI

```python
from fastapi import FastAPI
from app.core.error_handler_registry import setup_error_handling

app = FastAPI()

# Set up all error handlers and middleware
setup_error_handling(app)
```

### 5. FastAPI Route Example

```python
from fastapi import APIRouter
from app.core.exceptions import PartnerNotFound, ValidationError

router = APIRouter()

@router.get("/partners/{partner_id}")
async def get_partner(partner_id: str):
    # These exceptions will be automatically caught and converted
    # to appropriate HTTP responses by the global error handlers

    if not partner_id:
        raise ValidationError("Partner ID is required", field="partner_id")

    partner = await partner_service.get_by_id(partner_id)
    if not partner:
        raise PartnerNotFound(partner_id)

    return partner
```

## Error Response Format

All API errors return a consistent JSON structure:

```json
{
  "error": true,
  "message": "Partner with ID 'invalid_id' not found",
  "error_code": "NOT_FOUND",
  "error_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-15T10:30:00Z",
  "status_code": 404,
  "path": "/api/partners/invalid_id",
  "method": "GET",
  "request_id": "req_123456",
  "context": {
    "entity_type": "Partner",
    "entity_id": "invalid_id"
  }
}
```

### Validation Error Response

```json
{
  "error": true,
  "message": "Request validation failed",
  "error_code": "VALIDATION_ERROR",
  "error_id": "550e8400-e29b-41d4-a716-446655440001",
  "timestamp": "2024-01-15T10:30:00Z",
  "status_code": 422,
  "details": [
    {
      "field": "amount",
      "message": "Amount must be positive",
      "code": "positive_value",
      "value": "-100"
    }
  ],
  "field_errors": {
    "amount": ["Amount must be positive"]
  }
}
```

## Logging Output

Structured logs include comprehensive context:

```json
{
  "error": {
    "type": "PartnerNotFound",
    "message": "Partner with ID 'invalid_id' not found",
    "error_code": "NOT_FOUND",
    "error_id": "550e8400-e29b-41d4-a716-446655440000"
  },
  "context": {
    "request_id": "req_123456",
    "user_id": "user_789",
    "timestamp": "2024-01-15T10:30:00Z"
  },
  "traceback": "..." // Only in DEBUG mode
}
```

## Migration from Legacy System

The new system maintains backward compatibility with existing exception handlers. Legacy exceptions like `Advisor360Exception` are still supported but will be gradually migrated to the new system.

### Migration Steps

1. Replace legacy exceptions with new domain exceptions
2. Update error handling to use the new structured responses
3. Add proper error logging with context
4. Remove legacy exception handlers once migration is complete

## Best Practices

1. **Use Specific Exceptions**: Choose the most specific exception type for your use case
2. **Include Context**: Always provide relevant context in exception constructors
3. **Log Appropriately**: Use appropriate severity levels for different error types
4. **Preserve Stack Traces**: Include original exceptions when wrapping errors
5. **Don't Expose Internals**: Infrastructure errors should not expose sensitive details to clients
6. **Use Request Context**: Always set up error context for request tracing

## Testing

The error handling system supports easy testing through:

1. **Predictable Exception Types**: All exceptions have consistent interfaces
2. **Structured Data**: Exception data can be easily validated in tests
3. **Mock-Friendly Logging**: Error logger can be easily mocked for testing
4. **Consistent Responses**: API responses have predictable structures

Example test:

```python
def test_partner_not_found():
    with pytest.raises(PartnerNotFound) as exc_info:
        get_partner_by_id("nonexistent")

    assert exc_info.value.entity_type == "Partner"
    assert exc_info.value.entity_id == "nonexistent"
    assert exc_info.value.error_code == "NOT_FOUND"
```
