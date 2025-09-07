# Custom exceptions

# Domain exceptions
from .domain_exceptions import (
    AuthorizationError,
    BusinessRuleViolation,
    CommissionError,
    CommissionNotFound,
    ConfigurationError,
    DomainException,
    DuplicateError,
    ExternalServiceError,
    FinancialYearError,
    InvalidCommissionAmount,
    NotFoundError,
    PartnerError,
    PartnerHasCommissions,
    PartnerNotFound,
    TransactionError,
    TransactionNotFound,
    ValidationError,
)

# Infrastructure exceptions
from .infrastructure_exceptions import (
    CacheError,
    ConnectionError,
    DatabaseError,
    FileSystemError,
    InfrastructureError,
    SerializationError,
    SupabaseError,
    TimeoutError,
)

# Legacy repository exceptions (for backward compatibility)
from .repository_exceptions import ConfigurationError as LegacyConfigurationError
from .repository_exceptions import ConnectionError as LegacyConnectionError
from .repository_exceptions import DuplicateError as LegacyDuplicateError
from .repository_exceptions import NotFoundError as LegacyNotFoundError
from .repository_exceptions import RepositoryError
from .repository_exceptions import TransactionError as LegacyTransactionError
from .repository_exceptions import ValidationError as LegacyValidationError

__all__ = [
    # Domain exceptions
    "DomainException",
    "ValidationError",
    "NotFoundError",
    "BusinessRuleViolation",
    "DuplicateError",
    "AuthorizationError",
    "ConfigurationError",
    "ExternalServiceError",
    "FinancialYearError",
    "PartnerError",
    "PartnerNotFound",
    "PartnerHasCommissions",
    "CommissionError",
    "CommissionNotFound",
    "InvalidCommissionAmount",
    "TransactionError",
    "TransactionNotFound",
    # Infrastructure exceptions
    "InfrastructureError",
    "DatabaseError",
    "ConnectionError",
    "TimeoutError",
    "SupabaseError",
    "CacheError",
    "FileSystemError",
    "SerializationError",
    # Legacy exceptions (for backward compatibility)
    "RepositoryError",
    "LegacyNotFoundError",
    "LegacyValidationError",
    "LegacyDuplicateError",
    "LegacyConnectionError",
    "LegacyTransactionError",
    "LegacyConfigurationError",
]
