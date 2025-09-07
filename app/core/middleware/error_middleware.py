"""Error handling middleware for request context and error boundary.

This middleware provides request-level error handling, context management,
and ensures that all unhandled exceptions are properly caught and logged.
"""

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from ..exceptions.error_responses import InternalServerErrorResponse
from ..logging.error_logger import error_context, error_logger
from ..logging.structured_logger import get_logger


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for comprehensive error handling and request context management.

    This middleware:
    1. Generates unique request IDs for tracing
    2. Sets up error logging context
    3. Catches any unhandled exceptions
    4. Provides request timing information
    5. Ensures consistent error responses
    """

    def __init__(self, app, logger_name: str = "error_middleware"):
        """Initialize error handling middleware.

        Args:
            app: FastAPI application instance
            logger_name: Name for the middleware logger
        """
        super().__init__(app)
        self.logger = get_logger(logger_name)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with error handling and context management.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler

        Returns:
            HTTP response with proper error handling
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Extract user ID if available (from auth middleware)
        user_id = getattr(request.state, "user_id", None)

        # Record request start time
        start_time = time.time()

        # Set up error logging context
        with error_context(request_id=request_id, user_id=user_id):
            try:
                # Add request context to logs
                self.logger.info(
                    f"Request started: {request.method} {request.url.path}",
                    {
                        "request_id": request_id,
                        "method": request.method,
                        "path": str(request.url.path),
                        "user_id": user_id,
                        "user_agent": request.headers.get("user-agent"),
                        "remote_addr": request.client.host if request.client else None,
                        "event_type": "request_start",
                    },
                )

                # Process the request
                response = await call_next(request)

                # Calculate request duration
                duration = time.time() - start_time

                # Log successful request completion
                self.logger.info(
                    f"Request completed: {request.method} {request.url.path} - {response.status_code}",
                    {
                        "request_id": request_id,
                        "method": request.method,
                        "path": str(request.url.path),
                        "status_code": response.status_code,
                        "duration_ms": round(duration * 1000, 2),
                        "user_id": user_id,
                        "event_type": "request_success",
                    },
                )

                # Add request ID to response headers for tracing
                response.headers["X-Request-ID"] = request_id

                return response

            except Exception as exc:
                # Calculate request duration for failed requests
                duration = time.time() - start_time

                # Log the unhandled exception
                error_logger.log_critical_error(
                    exc,
                    system_impact="Unhandled exception in request processing",
                    recovery_action="Check application logs and fix the underlying issue",
                )

                # Log failed request
                self.logger.error(
                    f"Request failed: {request.method} {request.url.path} - Unhandled Exception",
                    {
                        "request_id": request_id,
                        "method": request.method,
                        "path": str(request.url.path),
                        "duration_ms": round(duration * 1000, 2),
                        "user_id": user_id,
                        "exception_type": exc.__class__.__name__,
                        "exception_message": str(exc),
                        "event_type": "request_error",
                    },
                    exc_info=True,
                )

                # Return generic error response
                error_response = InternalServerErrorResponse(
                    error_id=str(uuid.uuid4()),
                    status_code=500,
                    path=str(request.url.path),
                    method=request.method,
                    request_id=request_id,
                )

                response = JSONResponse(status_code=500, content=error_response.dict())
                response.headers["X-Request-ID"] = request_id

                return response


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Middleware for setting up request context and correlation IDs.

    This middleware extracts and sets up context information that can be
    used throughout the request lifecycle for logging and tracing.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Set up request context from headers and state.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler

        Returns:
            HTTP response with context headers
        """
        # Extract correlation ID from headers (for distributed tracing)
        correlation_id = request.headers.get("X-Correlation-ID")
        if correlation_id:
            request.state.correlation_id = correlation_id

        # Extract user ID from authorization headers if available
        # This would typically be set by an authentication middleware
        auth_header = request.headers.get("Authorization")
        if auth_header and not hasattr(request.state, "user_id"):
            # This is a placeholder - actual user extraction would depend on auth implementation
            request.state.user_id = None

        # Process the request
        response = await call_next(request)

        # Add correlation ID to response if it exists
        if correlation_id:
            response.headers["X-Correlation-ID"] = correlation_id

        return response
