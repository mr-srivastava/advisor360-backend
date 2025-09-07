"""Infrastructure-specific exceptions for external services and technical concerns.

This module defines exceptions related to infrastructure components like
databases, external APIs, file systems, and other technical concerns.
"""

from typing import Optional

from .domain_exceptions import DomainException


class InfrastructureError(DomainException):
    """Base exception for infrastructure-related errors.

    This is the base class for all exceptions related to infrastructure
    components like databases, external services, file systems, etc.
    """

    pass


class DatabaseError(InfrastructureError):
    """Exception raised when database operations fail.

    This should be raised for database connection issues, query failures,
    transaction problems, and other database-related errors.
    """

    def __init__(
        self,
        operation: str,
        message: Optional[str] = None,
        table: Optional[str] = None,
        query: Optional[str] = None,
        **kwargs,
    ):
        if not message:
            message = f"Database operation failed: {operation}"

        context = kwargs.get("context", {})
        context.update({"operation": operation, "table": table, "query": query})

        super().__init__(message, context=context, **kwargs)
        self.operation = operation
        self.table = table
        self.query = query


class ConnectionError(InfrastructureError):
    """Exception raised when there's a connection issue with external services.

    This should be raised when the application cannot connect to or
    communicate with external services like databases, APIs, etc.
    """

    def __init__(
        self,
        service: str,
        message: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        **kwargs,
    ):
        if not message:
            message = f"Failed to connect to {service}"
            if host:
                message += f" at {host}"
                if port:
                    message += f":{port}"

        context = kwargs.get("context", {})
        context.update({"service": service, "host": host, "port": port})

        super().__init__(message, context=context, **kwargs)
        self.service = service
        self.host = host
        self.port = port


class TimeoutError(InfrastructureError):
    """Exception raised when an operation times out.

    This should be raised when operations exceed their timeout limits.
    """

    def __init__(
        self,
        operation: str,
        timeout_seconds: float,
        message: Optional[str] = None,
        **kwargs,
    ):
        if not message:
            message = (
                f"Operation '{operation}' timed out after {timeout_seconds} seconds"
            )

        context = kwargs.get("context", {})
        context.update({"operation": operation, "timeout_seconds": timeout_seconds})

        super().__init__(message, context=context, **kwargs)
        self.operation = operation
        self.timeout_seconds = timeout_seconds


class SupabaseError(DatabaseError):
    """Exception raised for Supabase-specific errors.

    This should be raised for Supabase client errors, authentication issues,
    and Supabase-specific operation failures.
    """

    def __init__(
        self,
        operation: str,
        supabase_error: Optional[Exception] = None,
        status_code: Optional[int] = None,
        **kwargs,
    ):
        message = f"Supabase operation failed: {operation}"
        if status_code:
            message += f" (Status: {status_code})"

        context = kwargs.get("context", {})
        context.update({"supabase_operation": operation, "status_code": status_code})

        super().__init__(
            operation,
            message=message,
            context=context,
            original_error=supabase_error,
            **kwargs,
        )
        self.supabase_error = supabase_error
        self.status_code = status_code


class CacheError(InfrastructureError):
    """Exception raised for caching-related errors.

    This should be raised for cache connection issues, serialization problems,
    and other cache-related failures.
    """

    def __init__(
        self,
        operation: str,
        cache_key: Optional[str] = None,
        message: Optional[str] = None,
        **kwargs,
    ):
        if not message:
            message = f"Cache operation failed: {operation}"
            if cache_key:
                message += f" for key: {cache_key}"

        context = kwargs.get("context", {})
        context.update({"cache_operation": operation, "cache_key": cache_key})

        super().__init__(message, context=context, **kwargs)
        self.operation = operation
        self.cache_key = cache_key


class FileSystemError(InfrastructureError):
    """Exception raised for file system operations.

    This should be raised for file I/O errors, permission issues,
    and other file system related problems.
    """

    def __init__(
        self, operation: str, file_path: str, message: Optional[str] = None, **kwargs
    ):
        if not message:
            message = f"File system operation '{operation}' failed for: {file_path}"

        context = kwargs.get("context", {})
        context.update({"file_operation": operation, "file_path": file_path})

        super().__init__(message, context=context, **kwargs)
        self.operation = operation
        self.file_path = file_path


class SerializationError(InfrastructureError):
    """Exception raised for serialization/deserialization errors.

    This should be raised when data cannot be properly serialized or
    deserialized (JSON, XML, etc.).
    """

    def __init__(
        self,
        data_type: str,
        operation: str,  # 'serialize' or 'deserialize'
        message: Optional[str] = None,
        **kwargs,
    ):
        if not message:
            message = f"Failed to {operation} {data_type}"

        context = kwargs.get("context", {})
        context.update({"data_type": data_type, "serialization_operation": operation})

        super().__init__(message, context=context, **kwargs)
        self.data_type = data_type
        self.operation = operation
