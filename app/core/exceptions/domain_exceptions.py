"""Domain-specific exceptions for the application.

This module defines a comprehensive exception hierarchy that follows
domain-driven design principles and provides consistent error handling
across all layers of the application.
"""

import uuid
from datetime import datetime
from typing import Any, Optional


class DomainException(Exception):
    """Base exception for all domain-related errors.

    This is the root exception class that all domain exceptions inherit from.
    It provides common functionality like error codes, context, and metadata.
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
        self.original_error = original_error
        self.timestamp = datetime.utcnow()
        self.error_id = str(uuid.uuid4())

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for serialization."""
        return {
            "error": True,
            "message": self.message,
            "error_code": self.error_code,
            "error_id": self.error_id,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context,
        }


class ValidationError(DomainException):
    """Exception raised when data validation fails.

    This should be raised when input data doesn't meet validation rules,
    business constraints, or format requirements.
    """

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        validation_rule: Optional[str] = None,
        **kwargs,
    ):
        context = kwargs.get("context", {})
        if field:
            context["field"] = field
        if value is not None:
            context["value"] = str(value)
        if validation_rule:
            context["validation_rule"] = validation_rule

        super().__init__(message, context=context, **kwargs)
        self.field = field
        self.value = value
        self.validation_rule = validation_rule


class NotFoundError(DomainException):
    """Exception raised when a requested entity is not found.

    This should be raised when trying to access an entity that doesn't exist.
    """

    def __init__(
        self, entity_type: str, entity_id: str, message: Optional[str] = None, **kwargs
    ):
        if not message:
            message = f"{entity_type} with ID '{entity_id}' not found"

        context = kwargs.get("context", {})
        context.update({"entity_type": entity_type, "entity_id": entity_id})

        super().__init__(message, context=context, **kwargs)
        self.entity_type = entity_type
        self.entity_id = entity_id


class BusinessRuleViolation(DomainException):
    """Exception raised when a business rule is violated.

    This should be raised when an operation violates domain business rules
    or constraints that are not simple validation errors.
    """

    def __init__(self, rule_name: str, message: str, **kwargs):
        context = kwargs.get("context", {})
        context["rule_name"] = rule_name

        super().__init__(message, context=context, **kwargs)
        self.rule_name = rule_name


class DuplicateError(DomainException):
    """Exception raised when trying to create an entity that already exists.

    This should be raised when trying to create an entity with a unique
    constraint violation.
    """

    def __init__(
        self,
        entity_type: str,
        field: str,
        value: str,
        message: Optional[str] = None,
        **kwargs,
    ):
        if not message:
            message = f"{entity_type} with {field} '{value}' already exists"

        context = kwargs.get("context", {})
        context.update({"entity_type": entity_type, "field": field, "value": value})

        super().__init__(message, context=context, **kwargs)
        self.entity_type = entity_type
        self.field = field
        self.value = value


class AuthorizationError(DomainException):
    """Exception raised when a user is not authorized to perform an action.

    This should be raised when access control rules prevent an operation.
    """

    def __init__(
        self,
        action: str,
        resource: Optional[str] = None,
        user_id: Optional[str] = None,
        message: Optional[str] = None,
        **kwargs,
    ):
        if not message:
            message = f"Not authorized to perform action: {action}"
            if resource:
                message += f" on resource: {resource}"

        context = kwargs.get("context", {})
        context.update({"action": action, "resource": resource, "user_id": user_id})

        super().__init__(message, context=context, **kwargs)
        self.action = action
        self.resource = resource
        self.user_id = user_id


class ConfigurationError(DomainException):
    """Exception raised when there's a configuration issue.

    This should be raised when the application is misconfigured or
    missing required configuration parameters.
    """

    def __init__(self, config_key: str, message: Optional[str] = None, **kwargs):
        if not message:
            message = f"Configuration error for key: {config_key}"

        context = kwargs.get("context", {})
        context["config_key"] = config_key

        super().__init__(message, context=context, **kwargs)
        self.config_key = config_key


class ExternalServiceError(DomainException):
    """Exception raised when an external service call fails.

    This should be raised when communication with external services
    (databases, APIs, etc.) fails.
    """

    def __init__(
        self,
        service_name: str,
        operation: str,
        message: Optional[str] = None,
        status_code: Optional[int] = None,
        **kwargs,
    ):
        if not message:
            message = f"External service '{service_name}' failed during operation: {operation}"

        context = kwargs.get("context", {})
        context.update(
            {
                "service_name": service_name,
                "operation": operation,
                "status_code": status_code,
            }
        )

        super().__init__(message, context=context, **kwargs)
        self.service_name = service_name
        self.operation = operation
        self.status_code = status_code


# Specific domain exceptions for the application


class FinancialYearError(ValidationError):
    """Exception raised for financial year related errors."""

    def __init__(self, financial_year: str, message: Optional[str] = None, **kwargs):
        if not message:
            message = f"Invalid financial year: {financial_year}"
        super().__init__(
            message, field="financial_year", value=financial_year, **kwargs
        )


class PartnerError(DomainException):
    """Base exception for partner-related errors."""

    pass


class PartnerNotFound(NotFoundError):
    """Exception raised when a partner is not found."""

    def __init__(self, partner_id: str, **kwargs):
        super().__init__("Partner", partner_id, **kwargs)


class PartnerHasCommissions(BusinessRuleViolation):
    """Exception raised when trying to delete a partner that has commissions."""

    def __init__(self, partner_id: str, commission_count: int, **kwargs):
        message = f"Cannot delete partner {partner_id}: has {commission_count} associated commissions"
        context = kwargs.get("context", {})
        context.update({"partner_id": partner_id, "commission_count": commission_count})
        super().__init__("partner_has_commissions", message, context=context, **kwargs)


class CommissionError(DomainException):
    """Base exception for commission-related errors."""

    pass


class CommissionNotFound(NotFoundError):
    """Exception raised when a commission is not found."""

    def __init__(self, commission_id: str, **kwargs):
        super().__init__("Commission", commission_id, **kwargs)


class InvalidCommissionAmount(ValidationError):
    """Exception raised when commission amount is invalid."""

    def __init__(self, amount: float, **kwargs):
        message = f"Invalid commission amount: {amount}. Amount must be positive."
        super().__init__(
            message,
            field="amount",
            value=amount,
            validation_rule="positive_amount",
            **kwargs,
        )


class TransactionError(DomainException):
    """Base exception for transaction-related errors."""

    pass


class TransactionNotFound(NotFoundError):
    """Exception raised when a transaction is not found."""

    def __init__(self, transaction_id: str, **kwargs):
        super().__init__("Transaction", transaction_id, **kwargs)
