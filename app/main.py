from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import commissions, partners, dashboard
from app.core.error_handlers import (
    domain_exception_handler,
    infrastructure_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler
)
from app.core.exceptions import (
    DomainException,
    FinancialYearError,
    PartnerNotFound,
    CommissionNotFound,
    ValidationError,
    DatabaseError
)
from app.core.middleware import (
    ErrorHandlingMiddleware,
    RequestContextMiddleware,
    RequestLoggingMiddleware,
    MetricsMiddleware
)
from app.core.logging.config import setup_logging
from app.core.config.app_config import get_config
from app.core.bootstrap import setup_application
import logging

# Initialize logging configuration
setup_logging()

# Get application configuration
config = get_config()

# Bootstrap application dependencies
container = setup_application()

app = FastAPI(
    title="Advisor360 API",
    description="Financial advisory platform API for tracking commissions and partner relationships",
    version="1.0.0"
)

# Add middleware in reverse order (last added = first executed)
# Error handling middleware (outermost)
app.add_middleware(ErrorHandlingMiddleware)

# Metrics collection middleware
app.add_middleware(MetricsMiddleware)

# Request logging middleware
app.add_middleware(
    RequestLoggingMiddleware,
    log_request_body=True,
    log_response_body=config.is_development,  # Only log response bodies in development
    log_headers=True,
    slow_request_threshold_ms=1000.0
)

# Request context middleware
app.add_middleware(RequestContextMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=config.cors.credentials,
    allow_methods=config.cors.methods,
    allow_headers=config.cors.headers,
)

# Add exception handlers
app.add_exception_handler(DomainException, domain_exception_handler)
app.add_exception_handler(DatabaseError, infrastructure_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# include routers
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
app.include_router(partners.router, prefix="/partners", tags=["partners"])
app.include_router(commissions.router, prefix="/commissions", tags=["commissions"])

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from app.core.middleware.metrics_middleware import get_metrics_summary
    
    metrics = get_metrics_summary()
    
    return {
        "status": "healthy", 
        "service": "Advisor360 API",
        "version": "1.0.0",
        "environment": config.environment,
        "metrics": metrics['summary']
    }

@app.get("/metrics")
async def get_metrics():
    """Detailed metrics endpoint"""
    from app.core.middleware.metrics_middleware import get_metrics_summary
    
    return get_metrics_summary()


@app.on_event("startup")
async def startup_event():
    """Application startup event handler"""
    logger = logging.getLogger(__name__)
    logger.info("Application startup completed")
    logger.info(f"Dependency container initialized with {len(container._services)} services")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event handler"""
    logger = logging.getLogger(__name__)
    logger.info("Application shutdown initiated")
    
    # Clean up resources if needed
    container.clear()
    logger.info("Application shutdown completed")