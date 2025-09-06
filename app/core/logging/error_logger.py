"""
Error logging utilities with structured logging and context.

This module provides comprehensive error logging functionality with
proper context, severity levels, and structured data for better
debugging and monitoring.
"""

import logging
import traceback
import sys
from typing import Optional, Dict, Any, Union
from datetime import datetime
from contextlib import contextmanager
from contextvars import ContextVar
import json

from ..exceptions.domain_exceptions import DomainException
from ..exceptions.infrastructure_exceptions import InfrastructureError


# Context variables for request tracking
request_id_context: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_id_context: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
correlation_id_context: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)


class StructuredErrorLogger:
    """
    Structured error logger with context and severity management.
    
    This logger provides consistent error logging with structured data,
    context information, and appropriate severity levels.
    """
    
    def __init__(self, logger_name: str = "error_logger"):
        self.logger = logging.getLogger(logger_name)
        self._setup_logger()
    
    def _setup_logger(self):
        """Set up the logger with appropriate formatting."""
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def _get_context_data(self) -> Dict[str, Any]:
        """Get current context data from context variables."""
        return {
            'request_id': request_id_context.get(),
            'user_id': user_id_context.get(),
            'correlation_id': correlation_id_context.get(),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _create_log_data(
        self,
        exception: Exception,
        context: Optional[Dict[str, Any]] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create structured log data for an exception.
        
        Args:
            exception: The exception to log
            context: Additional context data
            extra_data: Extra data to include in the log
            
        Returns:
            Dictionary with structured log data
        """
        log_data = {
            'error': {
                'type': exception.__class__.__name__,
                'message': str(exception),
                'module': exception.__class__.__module__,
            },
            'context': self._get_context_data(),
            'traceback': traceback.format_exc() if self.logger.isEnabledFor(logging.DEBUG) else None
        }
        
        # Add domain exception specific data
        if hasattr(exception, 'error_code') and hasattr(exception, 'error_id'):
            log_data['error'].update({
                'error_code': getattr(exception, 'error_code', None),
                'error_id': getattr(exception, 'error_id', None),
                'domain_context': getattr(exception, 'context', None),
                'original_error': str(getattr(exception, 'original_error', None)) if getattr(exception, 'original_error', None) else None
            })
        
        # Add infrastructure exception specific data
        if 'infrastructure' in exception.__class__.__module__.lower():
            log_data['error']['infrastructure_error'] = True
        
        # Add additional context
        if context:
            log_data['context'].update(context)
        
        # Add extra data
        if extra_data:
            log_data.update(extra_data)
        
        return log_data
    
    def log_error(
        self,
        exception: Exception,
        severity: str = "ERROR",
        context: Optional[Dict[str, Any]] = None,
        extra_data: Optional[Dict[str, Any]] = None,
        include_traceback: bool = True
    ):
        """
        Log an error with structured data and appropriate severity.
        
        Args:
            exception: The exception to log
            severity: Log severity level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            context: Additional context data
            extra_data: Extra data to include in the log
            include_traceback: Whether to include traceback in the log
        """
        log_data = self._create_log_data(exception, context, extra_data)
        
        if not include_traceback:
            log_data.pop('traceback', None)
        
        # Determine severity based on exception type if not specified
        if severity == "ERROR":
            if 'ValidationError' in exception.__class__.__name__ or 'NotFoundError' in exception.__class__.__name__:
                severity = "WARNING"
            elif 'BusinessRule' in exception.__class__.__name__:
                severity = "ERROR"
            elif 'infrastructure' in exception.__class__.__module__.lower():
                severity = "ERROR"
            elif "Internal" in str(exception):
                severity = "CRITICAL"
        
        # Log with appropriate level
        log_level = getattr(logging, severity.upper(), logging.ERROR)
        self.logger.log(
            log_level,
            f"Exception occurred: {exception.__class__.__name__}",
            extra={'structured_data': json.dumps(log_data, default=str)}
        )
    
    def log_validation_error(
        self,
        exception: Exception,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        validation_rule: Optional[str] = None
    ):
        """
        Log a validation error with specific validation context.
        
        Args:
            exception: The validation exception
            field: The field that failed validation
            value: The invalid value
            validation_rule: The validation rule that was violated
        """
        context = {
            'validation': {
                'field': field,
                'value': str(value) if value is not None else None,
                'rule': validation_rule
            }
        }
        self.log_error(exception, severity="WARNING", context=context)
    
    def log_business_rule_violation(
        self,
        exception: Exception,
        rule_name: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None
    ):
        """
        Log a business rule violation with business context.
        
        Args:
            exception: The business rule exception
            rule_name: Name of the violated rule
            entity_type: Type of entity involved
            entity_id: ID of entity involved
        """
        context = {
            'business_rule': {
                'rule_name': rule_name,
                'entity_type': entity_type,
                'entity_id': entity_id
            }
        }
        self.log_error(exception, severity="ERROR", context=context)
    
    def log_infrastructure_error(
        self,
        exception: Exception,
        service: str,
        operation: Optional[str] = None,
        retry_count: Optional[int] = None
    ):
        """
        Log an infrastructure error with service context.
        
        Args:
            exception: The infrastructure exception
            service: Name of the service that failed
            operation: The operation that failed
            retry_count: Number of retries attempted
        """
        context = {
            'infrastructure': {
                'service': service,
                'operation': operation,
                'retry_count': retry_count
            }
        }
        self.log_error(exception, severity="ERROR", context=context)
    
    def log_critical_error(
        self,
        exception: Exception,
        system_impact: str,
        recovery_action: Optional[str] = None
    ):
        """
        Log a critical error that requires immediate attention.
        
        Args:
            exception: The critical exception
            system_impact: Description of system impact
            recovery_action: Suggested recovery action
        """
        context = {
            'critical': {
                'system_impact': system_impact,
                'recovery_action': recovery_action,
                'requires_immediate_attention': True
            }
        }
        self.log_error(exception, severity="CRITICAL", context=context)


# Global error logger instance
error_logger = StructuredErrorLogger()


@contextmanager
def error_context(
    request_id: Optional[str] = None,
    user_id: Optional[str] = None,
    correlation_id: Optional[str] = None
):
    """
    Context manager for setting error logging context.
    
    Args:
        request_id: Request identifier
        user_id: User identifier
        correlation_id: Correlation identifier for distributed tracing
    """
    # Set context variables
    request_token = request_id_context.set(request_id) if request_id else None
    user_token = user_id_context.set(user_id) if user_id else None
    correlation_token = correlation_id_context.set(correlation_id) if correlation_id else None
    
    try:
        yield
    finally:
        # Reset context variables
        if request_token:
            request_id_context.reset(request_token)
        if user_token:
            user_id_context.reset(user_token)
        if correlation_token:
            correlation_id_context.reset(correlation_token)


def log_exception(
    exception: Exception,
    severity: str = "ERROR",
    context: Optional[Dict[str, Any]] = None,
    **kwargs
):
    """
    Convenience function for logging exceptions.
    
    Args:
        exception: The exception to log
        severity: Log severity level
        context: Additional context data
        **kwargs: Additional keyword arguments for the logger
    """
    error_logger.log_error(exception, severity, context, **kwargs)