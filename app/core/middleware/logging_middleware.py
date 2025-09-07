"""
Request/Response Logging Middleware

Middleware for comprehensive request and response logging with
structured data, timing metrics, and configurable detail levels.
"""

import uuid
import time
import json
from typing import Callable, Dict, Any, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse

from ..logging.request_logger import RequestLogger
from ..config.app_config import get_config


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for detailed request and response logging.
    
    Logs all HTTP requests and responses with structured data including:
    - Request details (method, path, headers, body)
    - Response details (status, headers, body)
    - Timing metrics and performance data
    - User context and correlation IDs
    - Error information for failed requests
    """
    
    def __init__(
        self,
        app,
        logger_name: str = "request_logger",
        log_request_body: bool = True,
        log_response_body: bool = False,
        log_headers: bool = True,
        slow_request_threshold_ms: float = 1000.0,
        max_body_size: int = 1000
    ):
        """
        Initialize request logging middleware.
        
        Args:
            app: FastAPI application instance
            logger_name: Name for the request logger
            log_request_body: Whether to log request bodies
            log_response_body: Whether to log response bodies
            log_headers: Whether to log request/response headers
            slow_request_threshold_ms: Threshold for slow request warnings
            max_body_size: Maximum body size to log in bytes
        """
        super().__init__(app)
        self.request_logger = RequestLogger(logger_name)
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.log_headers = log_headers
        self.slow_request_threshold_ms = slow_request_threshold_ms
        self.max_body_size = max_body_size
        
        # Get configuration
        self.config = get_config()
    
    async def _read_request_body(self, request: Request) -> Optional[bytes]:
        """
        Read request body if logging is enabled.
        
        Args:
            request: HTTP request
            
        Returns:
            Optional[bytes]: Request body or None
        """
        if not self.log_request_body:
            return None
        
        try:
            body = await request.body()
            return body if len(body) <= self.max_body_size else body[:self.max_body_size]
        except Exception:
            return None
    
    async def _read_response_body(self, response: Response) -> Optional[bytes]:
        """
        Read response body if logging is enabled.
        
        Args:
            response: HTTP response
            
        Returns:
            Optional[bytes]: Response body or None
        """
        if not self.log_response_body:
            return None
        
        try:
            if hasattr(response, 'body'):
                body = response.body
                return body if len(body) <= self.max_body_size else body[:self.max_body_size]
        except Exception:
            pass
        
        return None
    
    def _extract_request_data(self, request: Request, body: Optional[bytes] = None) -> Dict[str, Any]:
        """
        Extract relevant data from request for logging.
        
        Args:
            request: HTTP request
            body: Request body
            
        Returns:
            Dict[str, Any]: Request data for logging
        """
        data = {
            'method': request.method,
            'path': str(request.url.path),
            'query_params': dict(request.query_params) if request.query_params else None,
            'user_agent': request.headers.get('user-agent'),
            'remote_addr': request.client.host if request.client else None,
            'content_type': request.headers.get('content-type'),
            'content_length': request.headers.get('content-length')
        }
        
        # Add headers if enabled
        if self.log_headers:
            data['headers'] = dict(request.headers)
        
        # Add body if available and enabled
        if body and self.log_request_body:
            try:
                # Try to decode as JSON for better logging
                body_str = body.decode('utf-8')
                try:
                    data['body'] = json.loads(body_str)
                except json.JSONDecodeError:
                    data['body'] = body_str
            except UnicodeDecodeError:
                data['body'] = f"<binary data: {len(body)} bytes>"
        
        return data
    
    def _extract_response_data(self, response: Response, body: Optional[bytes] = None) -> Dict[str, Any]:
        """
        Extract relevant data from response for logging.
        
        Args:
            response: HTTP response
            body: Response body
            
        Returns:
            Dict[str, Any]: Response data for logging
        """
        data = {
            'status_code': response.status_code,
            'content_type': response.headers.get('content-type'),
            'content_length': response.headers.get('content-length')
        }
        
        # Add headers if enabled
        if self.log_headers:
            data['headers'] = dict(response.headers)
        
        # Add body if available and enabled
        if body and self.log_response_body:
            try:
                # Try to decode as JSON for better logging
                body_str = body.decode('utf-8')
                try:
                    data['body'] = json.loads(body_str)
                except json.JSONDecodeError:
                    data['body'] = body_str
            except UnicodeDecodeError:
                data['body'] = f"<binary data: {len(body)} bytes>"
        
        return data
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with comprehensive logging.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler
            
        Returns:
            HTTP response with logging
        """
        # Generate request ID if not already present
        request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
        request.state.request_id = request_id
        
        # Extract user context
        user_id = getattr(request.state, 'user_id', None)
        correlation_id = getattr(request.state, 'correlation_id', None)
        
        # Read request body if needed
        request_body = await self._read_request_body(request)
        
        # Extract request data
        request_data = self._extract_request_data(request, request_body)
        
        # Log request start
        start_time = self.request_logger.log_request_start(
            request_id=request_id,
            method=request.method,
            path=str(request.url.path),
            query_params=request_data.get('query_params'),
            headers=request_data.get('headers') if self.log_headers else None,
            body=request_data.get('body'),
            user_id=user_id,
            user_agent=request_data.get('user_agent'),
            remote_addr=request_data.get('remote_addr'),
            correlation_id=correlation_id
        )
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Read response body if needed
            response_body = await self._read_response_body(response)
            
            # Extract response data
            response_data = self._extract_response_data(response, response_body)
            
            # Calculate duration
            duration_ms = round((time.time() - start_time) * 1000, 2)
            
            # Log request completion
            self.request_logger.log_request_end(
                request_id=request_id,
                method=request.method,
                path=str(request.url.path),
                status_code=response.status_code,
                start_time=start_time,
                response_headers=response_data.get('headers') if self.log_headers else None,
                response_body=response_data.get('body'),
                user_id=user_id
            )
            
            # Log slow request warning if applicable
            if duration_ms > self.slow_request_threshold_ms:
                self.request_logger.log_slow_request(
                    request_id=request_id,
                    method=request.method,
                    path=str(request.url.path),
                    duration_ms=duration_ms,
                    threshold_ms=self.slow_request_threshold_ms,
                    additional_context={
                        'status_code': response.status_code,
                        'user_id': user_id
                    }
                )
            
            return response
            
        except Exception as exc:
            # Calculate duration for failed requests
            duration_ms = round((time.time() - start_time) * 1000, 2)
            
            # Log request failure
            self.request_logger.log_request_end(
                request_id=request_id,
                method=request.method,
                path=str(request.url.path),
                status_code=500,
                start_time=start_time,
                user_id=user_id,
                error=str(exc)
            )
            
            # Re-raise the exception to be handled by error middleware
            raise


class ResponseBodyLoggingMiddleware(BaseHTTPMiddleware):
    """
    Specialized middleware for capturing response bodies from streaming responses.
    
    This middleware handles the complexity of reading response bodies from
    StreamingResponse objects without interfering with the response stream.
    """
    
    def __init__(self, app, max_body_size: int = 1000):
        """
        Initialize response body logging middleware.
        
        Args:
            app: FastAPI application instance
            max_body_size: Maximum response body size to capture
        """
        super().__init__(app)
        self.max_body_size = max_body_size
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and capture response body for logging.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler
            
        Returns:
            HTTP response with body capture
        """
        response = await call_next(request)
        
        # Only capture body for specific conditions (errors, debug mode, etc.)
        should_capture = (
            response.status_code >= 400 or
            getattr(request.state, 'log_response_body', False)
        )
        
        if should_capture and isinstance(response, StreamingResponse):
            # Capture streaming response body
            body_parts = []
            total_size = 0
            
            async for chunk in response.body_iterator:
                if total_size + len(chunk) <= self.max_body_size:
                    body_parts.append(chunk)
                    total_size += len(chunk)
                else:
                    # Truncate if too large
                    remaining = self.max_body_size - total_size
                    if remaining > 0:
                        body_parts.append(chunk[:remaining])
                    break
            
            # Store captured body in request state for logging
            captured_body = b''.join(body_parts)
            request.state.response_body = captured_body
            
            # Create new response with the same content
            async def generate():
                for part in body_parts:
                    yield part
                # Continue with remaining chunks if not fully captured
                if total_size < self.max_body_size:
                    async for chunk in response.body_iterator:
                        yield chunk
            
            return StreamingResponse(
                generate(),
                status_code=response.status_code,
                headers=response.headers,
                media_type=response.media_type
            )
        
        return response