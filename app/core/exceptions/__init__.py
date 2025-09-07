# Custom exceptions

# Domain exceptions
from .domain_exceptions import (
    DomainException,
    ValidationError,
    NotFoundError,
    BusinessRuleViolation,
    DuplicateError,
    AuthorizationError,
    ConfigurationError,
    ExternalServiceError,
    FinancialYearError,
    PartnerError,
    PartnerNotFound,
    PartnerHasCommissions,
    CommissionError,
    CommissionNotFound,
    InvalidCommissionAmount,
    TransactionError,
    TransactionNotFound
)

# Infrastructure exceptions
from .infrastructure_exceptions import (
    InfrastructureError,
    DatabaseError,
    ConnectionError,
    TimeoutError,
    SupabaseError,
    CacheError,
    FileSystemError,
    SerializationError
)

# Legacy repository exceptions (for backward compatibility)
from .repository_exceptions import (
    RepositoryError,
    NotFoundError as LegacyNotFoundError,
    ValidationError as LegacyValidationError,
    DuplicateError as LegacyDuplicateError,
    ConnectionError as LegacyConnectionError,
    TransactionError as LegacyTransactionError,
    ConfigurationError as LegacyConfigurationError
)

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
    "LegacyConfigurationError"
]