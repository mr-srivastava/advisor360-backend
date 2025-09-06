"""
Request Logging Utilities

Specialized logging for HTTP requests and responses with metrics,
timing information, and structured data for observability.
"""

import time
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

from .structured_logger import get_logger, set_request_context, clear_request_context


class RequestLogger:
    """
    Specialized logger for HTTP request/response logging.
    
    Provides detailed logging of HTTP requests including timing,
    headers, body data (when appropriate), and response metrics.
    """
    
    def __init__(self, logger_name: str = "request_logger"):
        """
        Initialize request logger.
        
        Args:
            logger_name: Name for the logger instance
        """
        self.logger = get_logger(logger_name)
        self.sensitive_headers = {
            'authorization', 'cookie', 'x-api-key', 'x-auth-token',
            'x-access-token', 'x-refresh-token'
        }
        self.sensitive_fields = {
            'password', 'token', 'secret', 'key', 'auth', 'credential'
        }
    
    def _sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """
        Sanitize headers by masking sensitive values.
        
        Args:
            headers: Request/response headers
            
        Returns:
            Dict[str, str]: Sanitized headers
        """
        sanitized = {}
        for key, value in headers.items():
            if key.lower() in self.sensitive_headers:
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = value
        return sanitized
    
    def _sanitize_body(self, body: Any, max_size: int = 1000) -> Any:
        """
        Sanitize request/response body by removing sensitive data.
        
        Args:
            body: Request/response body
            max_size: Maximum body size to log
            
        Returns:
            Any: Sanitized body data
        """
        if body is None:
            return None
        
        # Convert to string if not already
        body_str = str(body) if not isinstance(body, str) else body
        
        # Truncate if too large
        if len(body_str) > max_size:
            body_str = body_str[:max_size] + "... [TRUNCATED]"
        
        # Try to parse as JSON for better sanitization
        try:
            body_data = json.loads(body_str)
            if isinstance(body_data, dict):
                return self._sanitize_dict(body_data)
            return body_data
        except (json.JSONDecodeError, TypeError):
            # Return as string if not JSON
            return body_str
    
    def _sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize dictionary by masking sensitive fields.
        
        Args:
            data: Dictionary to sanitize
            
        Returns:
            Dict[str, Any]: Sanitized dictionary
        """
        sanitized = {}
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in self.sensitive_fields):
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_dict(value)
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                sanitized[key] = [self._sanitize_dict(item) if isinstance(item, dict) else item for item in value]
            else:
                sanitized[key] = value
        return sanitized
    
    def log_request_start(
        self,
        request_id: str,
        method: str,
        path: str,
        query_params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Any] = None,
        user_id: Optional[str] = None,
        user_agent: Optional[str] = None,
        remote_addr: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> float:
        """
        Log request start and return start time.
        
        Args:
            request_id: Unique request identifier
            method: HTTP method
            path: Request path
            query_params: Query parameters
            headers: Request headers
            body: Request body
            user_id: User identifier
            user_agent: User agent string
            remote_addr: Remote IP address
            correlation_id: Correlation ID for distributed tracing
            
        Returns:
            float: Request start time for duration calculation
        """
        start_time = time.time()
        
        # Set request context for other loggers
        context = {
            'request_id': request_id,
            'user_id': user_id,
            'correlation_id': correlation_id,
            'method': method,
            'path': path
        }
        set_request_context(context)
        
        # Prepare log data
        log_data = {
            'request_id': request_id,
            'method': method,
            'path': path,
            'user_id': user_id,
            'user_agent': user_agent,
            'remote_addr': remote_addr,
            'correlation_id': correlation_id,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'event_type': 'request_start'
        }
        
        # Add query parameters if present
        if query_params:
            log_data['query_params'] = self._sanitize_dict(query_params)
        
        # Add sanitized headers
        if headers:
            log_data['headers'] = self._sanitize_headers(headers)
        
        # Add sanitized body for non-GET requests
        if body and method.upper() not in ['GET', 'HEAD', 'OPTIONS']:
            log_data['request_body'] = self._sanitize_body(body)
        
        self.logger.info(f"Request started: {method} {path}", log_data)
        return start_time
    
    def log_request_end(
        self,
        request_id: str,
        method: str,
        path: str,
        status_code: int,
        start_time: float,
        response_headers: Optional[Dict[str, str]] = None,
        response_body: Optional[Any] = None,
        user_id: Optional[str] = None,
        error: Optional[str] = None
    ):
        """
        Log request completion with response details.
        
        Args:
            request_id: Unique request identifier
            method: HTTP method
            path: Request path
            status_code: HTTP status code
            start_time: Request start time
            response_headers: Response headers
            response_body: Response body
            user_id: User identifier
            error: Error message if request failed
        """
        end_time = time.time()
        duration_ms = round((end_time - start_time) * 1000, 2)
        
        # Prepare log data
        log_data = {
            'request_id': request_id,
            'method': method,
            'path': path,
            'status_code': status_code,
            'duration_ms': duration_ms,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'event_type': 'request_end'
        }
        
        # Add response size if available
        if response_body:
            try:
                response_size = len(str(response_body))
                log_data['response_size'] = response_size
            except (TypeError, AttributeError):
                pass
        
        # Add sanitized response headers
        if response_headers:
            log_data['response_headers'] = self._sanitize_headers(response_headers)
        
        # Add sanitized response body for errors or debug mode
        if response_body and (status_code >= 400 or self.logger.logger.isEnabledFor(10)):  # DEBUG level
            log_data['response_body'] = self._sanitize_body(response_body, max_size=500)
        
        # Add error information
        if error:
            log_data['error'] = error
        
        # Log with appropriate level based on status code
        if status_code >= 500:
            self.logger.error(f"Request failed: {method} {path} - {status_code}", log_data)
        elif status_code >= 400:
            self.logger.warning(f"Request error: {method} {path} - {status_code}", log_data)
        else:
            self.logger.info(f"Request completed: {method} {path} - {status_code}", log_data)
        
        # Clear request context
        clear_request_context()
    
    def log_slow_request(
        self,
        request_id: str,
        method: str,
        path: str,
        duration_ms: float,
        threshold_ms: float = 1000.0,
        additional_context: Optional[Dict[str, Any]] = None
    ):
        """
        Log slow request warning.
        
        Args:
            request_id: Unique request identifier
            method: HTTP method
            path: Request path
            duration_ms: Request duration in milliseconds
            threshold_ms: Slow request threshold
            additional_context: Additional context data
        """
        log_data = {
            'request_id': request_id,
            'method': method,
            'path': path,
            'duration_ms': duration_ms,
            'threshold_ms': threshold_ms,
            'event_type': 'slow_request'
        }
        
        if additional_context:
            log_data.update(additional_context)
        
        self.logger.warning(
            f"Slow request detected: {method} {path} took {duration_ms}ms (threshold: {threshold_ms}ms)",
            log_data
        )
    
    def log_request_metrics(
        self,
        time_window: str,
        total_requests: int,
        avg_duration_ms: float,
        error_rate: float,
        status_code_distribution: Dict[str, int],
        top_endpoints: List[Dict[str, Any]]
    ):
        """
        Log aggregated request metrics.
        
        Args:
            time_window: Time window for metrics (e.g., "1h", "1d")
            total_requests: Total number of requests
            avg_duration_ms: Average request duration
            error_rate: Error rate percentage
            status_code_distribution: Distribution of status codes
            top_endpoints: Most frequently accessed endpoints
        """
        log_data = {
            'time_window': time_window,
            'total_requests': total_requests,
            'avg_duration_ms': avg_duration_ms,
            'error_rate': error_rate,
            'status_code_distribution': status_code_distribution,
            'top_endpoints': top_endpoints,
            'event_type': 'request_metrics'
        }
        
        self.logger.info(f"Request metrics for {time_window}: {total_requests} requests", log_data)