"""
Logging and monitoring middleware for FastAPI.
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import json

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging all HTTP requests and responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Log request and response details.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            HTTP response
        """
        # Generate request ID
        request_id = self._generate_request_id()

        # Log request
        start_time = time.time()

        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )

        # Process request
        try:
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Log response
            logger.info(
                f"[{request_id}] Status: {response.status_code} - "
                f"Duration: {duration:.3f}s"
            )

            # Add custom headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(duration)

            return response

        except Exception as e:
            duration = time.time() - start_time

            logger.error(
                f"[{request_id}] Error processing request: {str(e)} - "
                f"Duration: {duration:.3f}s"
            )
            raise

    def _generate_request_id(self) -> str:
        """Generate unique request ID."""
        import uuid
        return str(uuid.uuid4())[:8]


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for global error handling."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Handle errors gracefully.

        Args:
            request: Incoming request
            call_next: Next handler

        Returns:
            Response (error or success)
        """
        try:
            return await call_next(request)

        except ValueError as e:
            logger.error(f"ValueError: {str(e)}")
            return self._error_response(
                status_code=400,
                message="Invalid input",
                detail=str(e)
            )

        except PermissionError as e:
            logger.error(f"PermissionError: {str(e)}")
            return self._error_response(
                status_code=403,
                message="Permission denied",
                detail=str(e)
            )

        except FileNotFoundError as e:
            logger.error(f"FileNotFoundError: {str(e)}")
            return self._error_response(
                status_code=404,
                message="Resource not found",
                detail=str(e)
            )

        except Exception as e:
            logger.exception(f"Unhandled exception: {str(e)}")
            return self._error_response(
                status_code=500,
                message="Internal server error",
                detail=str(e) if logger.level == logging.DEBUG else "An error occurred"
            )

    def _error_response(self, status_code: int, message: str, detail: str) -> Response:
        """Create error response."""
        from fastapi.responses import JSONResponse

        return JSONResponse(
            status_code=status_code,
            content={
                "error": message,
                "detail": detail,
                "timestamp": time.time()
            }
        )


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting metrics."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.request_count = 0
        self.total_duration = 0.0
        self.endpoint_stats = {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Collect metrics for monitoring.

        Args:
            request: Incoming request
            call_next: Next handler

        Returns:
            Response with metrics
        """
        start_time = time.time()

        # Increment request count
        self.request_count += 1

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time
        self.total_duration += duration

        # Track endpoint stats
        endpoint = f"{request.method} {request.url.path}"
        if endpoint not in self.endpoint_stats:
            self.endpoint_stats[endpoint] = {
                "count": 0,
                "total_duration": 0.0,
                "avg_duration": 0.0
            }

        stats = self.endpoint_stats[endpoint]
        stats["count"] += 1
        stats["total_duration"] += duration
        stats["avg_duration"] = stats["total_duration"] / stats["count"]

        # Log slow requests (> 1 second)
        if duration > 1.0:
            logger.warning(
                f"Slow request: {endpoint} took {duration:.3f}s"
            )

        return response

    def get_metrics(self) -> dict:
        """Get current metrics."""
        return {
            "total_requests": self.request_count,
            "total_duration": round(self.total_duration, 3),
            "avg_duration": round(
                self.total_duration / self.request_count if self.request_count > 0 else 0,
                3
            ),
            "endpoints": self.endpoint_stats
        }


# Configure logging
def configure_logging(log_level: str = "INFO"):
    """
    Configure application logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Create formatters
    detailed_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    simple_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(simple_formatter)

    # File handler (detailed logs)
    file_handler = logging.FileHandler('app.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Silence noisy loggers
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('uvicorn.error').setLevel(logging.WARNING)

    logger.info(f"Logging configured at {log_level} level")
