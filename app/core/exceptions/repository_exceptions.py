"""
Repository-specific exceptions for data access layer error handling.
"""


class RepositoryError(Exception):
    """
    Base exception for repository operations.
    
    Raised when there's a general error in repository operations
    that doesn't fit into more specific categories.
    """
    
    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message)
        self.original_error = original_error


class NotFoundError(RepositoryError):
    """
    Exception raised when a requested entity is not found.
    
    This should be raised by repository methods when trying to access
    an entity that doesn't exist in the data store.
    """
    
    def __init__(self, entity_type: str, entity_id: str):
        message = f"{entity_type} with ID '{entity_id}' not found"
        super().__init__(message)
        self.entity_type = entity_type
        self.entity_id = entity_id


class ValidationError(RepositoryError):
    """
    Exception raised when entity data fails validation.
    
    This should be raised when trying to create or update an entity
    with invalid data that doesn't meet business rules or constraints.
    """
    
    def __init__(self, message: str, field: str = None, value: str = None):
        super().__init__(message)
        self.field = field
        self.value = value


class DuplicateError(RepositoryError):
    """
    Exception raised when trying to create an entity that already exists.
    
    This should be raised when trying to create an entity with a unique
    constraint violation (e.g., duplicate ID, unique name, etc.).
    """
    
    def __init__(self, entity_type: str, field: str, value: str):
        message = f"{entity_type} with {field} '{value}' already exists"
        super().__init__(message)
        self.entity_type = entity_type
        self.field = field
        self.value = value


class ConnectionError(RepositoryError):
    """
    Exception raised when there's a connection issue with the data store.
    
    This should be raised when the repository cannot connect to or
    communicate with the underlying data store.
    """
    
    def __init__(self, message: str = "Failed to connect to data store"):
        super().__init__(message)


class TransactionError(RepositoryError):
    """
    Exception raised when there's an error with database transactions.
    
    This should be raised when transaction operations fail, such as
    commit failures, rollback issues, or transaction timeout.
    """
    
    def __init__(self, message: str = "Transaction operation failed"):
        super().__init__(message)


class ConfigurationError(RepositoryError):
    """
    Exception raised when there's a configuration issue with the repository.
    
    This should be raised when the repository is misconfigured or
    missing required configuration parameters.
    """
    
    def __init__(self, message: str = "Repository configuration error"):
        super().__init__(message)