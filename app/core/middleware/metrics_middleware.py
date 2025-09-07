"""Metrics Collection Middleware

Middleware for collecting application metrics including request counts,
response times, error rates, and other performance indicators.
"""

import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Callable, DefaultDict, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..logging.structured_logger import get_logger


class MetricsCollector:
    """In-memory metrics collector for application performance data.

    Collects and aggregates metrics that can be used for monitoring,
    alerting, and performance analysis.
    """

    def __init__(self):
        """Initialize metrics collector."""
        self.request_count = 0
        self.error_count = 0
        self.total_response_time = 0.0
        self.status_codes: DefaultDict[int, int] = defaultdict(int)
        self.endpoints: DefaultDict[str, dict[str, Any]] = defaultdict(
            lambda: {"count": 0, "total_time": 0.0, "errors": 0, "avg_time": 0.0}
        )
        self.hourly_stats: DefaultDict[str, dict[str, Any]] = defaultdict(
            lambda: {"requests": 0, "errors": 0, "total_time": 0.0}
        )
        self.start_time = datetime.utcnow()

    def record_request(
        self,
        method: str,
        path: str,
        status_code: int,
        response_time_ms: float,
        user_id: Optional[str] = None,
    ):
        """Record a completed request.

        Args:
            method: HTTP method
            path: Request path
            status_code: HTTP status code
            response_time_ms: Response time in milliseconds
            user_id: User identifier
        """
        # Update global counters
        self.request_count += 1
        self.total_response_time += response_time_ms

        # Update error count
        if status_code >= 400:
            self.error_count += 1

        # Update status code distribution
        self.status_codes[status_code] += 1

        # Update endpoint-specific metrics
        endpoint_key = f"{method} {path}"
        endpoint_stats = self.endpoints[endpoint_key]
        endpoint_stats["count"] += 1
        endpoint_stats["total_time"] += response_time_ms
        endpoint_stats["avg_time"] = (
            endpoint_stats["total_time"] / endpoint_stats["count"]
        )

        if status_code >= 400:
            endpoint_stats["errors"] += 1

        # Update hourly statistics
        hour_key = datetime.utcnow().strftime("%Y-%m-%d %H:00")
        hourly_stats = self.hourly_stats[hour_key]
        hourly_stats["requests"] += 1
        hourly_stats["total_time"] += response_time_ms

        if status_code >= 400:
            hourly_stats["errors"] += 1

    def get_summary(self) -> dict[str, Any]:
        """Get summary metrics.

        Returns:
            Dict[str, Any]: Summary metrics
        """
        uptime = datetime.utcnow() - self.start_time
        avg_response_time = (
            self.total_response_time / self.request_count
            if self.request_count > 0
            else 0.0
        )
        error_rate = (
            (self.error_count / self.request_count) * 100
            if self.request_count > 0
            else 0.0
        )

        return {
            "uptime_seconds": uptime.total_seconds(),
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "error_rate_percent": round(error_rate, 2),
            "avg_response_time_ms": round(avg_response_time, 2),
            "requests_per_second": round(
                (
                    self.request_count / uptime.total_seconds()
                    if uptime.total_seconds() > 0
                    else 0.0
                ),
                2,
            ),
            "status_code_distribution": dict(self.status_codes),
        }

    def get_top_endpoints(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get top endpoints by request count.

        Args:
            limit: Maximum number of endpoints to return

        Returns:
            List[Dict[str, Any]]: Top endpoints with metrics
        """
        sorted_endpoints = sorted(
            self.endpoints.items(), key=lambda x: x[1]["count"], reverse=True
        )

        return [
            {
                "endpoint": endpoint,
                "count": stats["count"],
                "avg_time_ms": round(stats["avg_time"], 2),
                "errors": stats["errors"],
                "error_rate_percent": round(
                    (
                        (stats["errors"] / stats["count"]) * 100
                        if stats["count"] > 0
                        else 0.0
                    ),
                    2,
                ),
            }
            for endpoint, stats in sorted_endpoints[:limit]
        ]

    def get_hourly_stats(self, hours: int = 24) -> list[dict[str, Any]]:
        """Get hourly statistics for the last N hours.

        Args:
            hours: Number of hours to include

        Returns:
            List[Dict[str, Any]]: Hourly statistics
        """
        now = datetime.utcnow()
        stats = []

        for i in range(hours):
            hour = now - timedelta(hours=i)
            hour_key = hour.strftime("%Y-%m-%d %H:00")
            hour_stats = self.hourly_stats.get(
                hour_key, {"requests": 0, "errors": 0, "total_time": 0.0}
            )

            avg_time = (
                hour_stats["total_time"] / hour_stats["requests"]
                if hour_stats["requests"] > 0
                else 0.0
            )

            stats.append(
                {
                    "hour": hour_key,
                    "requests": hour_stats["requests"],
                    "errors": hour_stats["errors"],
                    "avg_time_ms": round(avg_time, 2),
                    "error_rate_percent": round(
                        (
                            (hour_stats["errors"] / hour_stats["requests"]) * 100
                            if hour_stats["requests"] > 0
                            else 0.0
                        ),
                        2,
                    ),
                }
            )

        return list(reversed(stats))


# Global metrics collector instance
metrics_collector = MetricsCollector()


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting application metrics.

    Collects performance metrics for all requests including timing,
    status codes, error rates, and endpoint-specific statistics.
    """

    def __init__(
        self, app, logger_name: str = "metrics_logger", log_interval_minutes: int = 60
    ):
        """Initialize metrics middleware.

        Args:
            app: FastAPI application instance
            logger_name: Name for the metrics logger
            log_interval_minutes: Interval for logging metrics summary
        """
        super().__init__(app)
        self.logger = get_logger(logger_name)
        self.log_interval_minutes = log_interval_minutes
        self.last_log_time = datetime.utcnow()

    def _should_log_metrics(self) -> bool:
        """Check if metrics should be logged based on interval.

        Returns:
            bool: True if metrics should be logged
        """
        now = datetime.utcnow()
        return (now - self.last_log_time).total_seconds() >= (
            self.log_interval_minutes * 60
        )

    def _log_metrics_summary(self):
        """Log metrics summary."""
        summary = metrics_collector.get_summary()
        top_endpoints = metrics_collector.get_top_endpoints(5)

        self.logger.info(
            "Application metrics summary",
            {
                "metrics_summary": summary,
                "top_endpoints": top_endpoints,
                "event_type": "metrics_summary",
            },
        )

        self.last_log_time = datetime.utcnow()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and collect metrics.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler

        Returns:
            HTTP response with metrics collection
        """
        start_time = time.time()

        try:
            # Process the request
            response = await call_next(request)

            # Calculate response time
            response_time_ms = round((time.time() - start_time) * 1000, 2)

            # Extract user context
            user_id = getattr(request.state, "user_id", None)

            # Record metrics
            metrics_collector.record_request(
                method=request.method,
                path=str(request.url.path),
                status_code=response.status_code,
                response_time_ms=response_time_ms,
                user_id=user_id,
            )

            # Log metrics summary if interval has passed
            if self._should_log_metrics():
                self._log_metrics_summary()

            return response

        except Exception:
            # Record failed request metrics
            response_time_ms = round((time.time() - start_time) * 1000, 2)
            user_id = getattr(request.state, "user_id", None)

            metrics_collector.record_request(
                method=request.method,
                path=str(request.url.path),
                status_code=500,
                response_time_ms=response_time_ms,
                user_id=user_id,
            )

            # Re-raise the exception
            raise


def get_metrics_summary() -> dict[str, Any]:
    """Get current metrics summary.

    Returns:
        Dict[str, Any]: Current metrics summary
    """
    return {
        "summary": metrics_collector.get_summary(),
        "top_endpoints": metrics_collector.get_top_endpoints(),
        "hourly_stats": metrics_collector.get_hourly_stats(),
    }
