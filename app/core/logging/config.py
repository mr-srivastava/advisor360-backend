"""
Logging Configuration Setup

Centralized logging configuration that sets up structured logging
with configurable levels, formatters, and output destinations.
"""

import logging
import sys
from typing import Optional, Dict, Any
from logging.handlers import RotatingFileHandler

from ..config.app_config import get_config, LoggingConfig
from .structured_logger import JSONFormatter


def setup_logging(config: Optional[LoggingConfig] = None) -> None:
    """
    Set up application-wide logging configuration.
    
    Args:
        config: Optional logging configuration override
    """
    if config is None:
        app_config = get_config()
        config = app_config.logging
    
    # Set root logger level
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config.level.upper(), logging.INFO))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler with JSON formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JSONFormatter())
    console_handler.setLevel(getattr(logging, config.level.upper(), logging.INFO))
    root_logger.addHandler(console_handler)
    
    # File handler if configured
    if config.file_path:
        file_handler = RotatingFileHandler(
            config.file_path,
            maxBytes=config.max_file_size,
            backupCount=config.backup_count
        )
        file_handler.setFormatter(JSONFormatter())
        file_handler.setLevel(getattr(logging, config.level.upper(), logging.INFO))
        root_logger.addHandler(file_handler)
    
    # Configure specific loggers
    configure_logger_levels(config.level)
    
    # Log configuration setup
    setup_logger = logging.getLogger("logging_setup")
    setup_logger.info(
        "Logging configuration initialized",
        extra={
            'extra_data': {
                'log_level': config.level,
                'file_path': config.file_path,
                'max_file_size': config.max_file_size,
                'backup_count': config.backup_count,
                'event_type': 'logging_setup'
            }
        }
    )


def configure_logger_levels(base_level: str) -> None:
    """
    Configure specific logger levels based on the base level.
    
    Args:
        base_level: Base logging level
    """
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    base_level_int = level_map.get(base_level.upper(), logging.INFO)
    
    # Configure third-party library loggers
    third_party_loggers = {
        'uvicorn': max(logging.INFO, base_level_int),
        'uvicorn.access': max(logging.WARNING, base_level_int),
        'fastapi': max(logging.INFO, base_level_int),
        'httpx': max(logging.WARNING, base_level_int),
        'supabase': max(logging.INFO, base_level_int),
        'postgrest': max(logging.WARNING, base_level_int)
    }
    
    for logger_name, level in third_party_loggers.items():
        logging.getLogger(logger_name).setLevel(level)
    
    # Configure application loggers
    app_loggers = {
        'request_logger': base_level_int,
        'error_logger': base_level_int,
        'metrics_logger': max(logging.INFO, base_level_int),
        'database_logger': base_level_int,
        'business_logger': base_level_int
    }
    
    for logger_name, level in app_loggers.items():
        logging.getLogger(logger_name).setLevel(level)


def get_logging_config() -> Dict[str, Any]:
    """
    Get current logging configuration.
    
    Returns:
        Dict[str, Any]: Current logging configuration
    """
    config = get_config().logging
    
    return {
        'level': config.level,
        'format': config.format,
        'file_path': config.file_path,
        'max_file_size': config.max_file_size,
        'backup_count': config.backup_count,
        'handlers': [
            handler.__class__.__name__ 
            for handler in logging.getLogger().handlers
        ]
    }


def update_log_level(level: str) -> None:
    """
    Update the logging level at runtime.
    
    Args:
        level: New logging level
    """
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if level.upper() not in valid_levels:
        raise ValueError(f"Invalid log level: {level}. Must be one of {valid_levels}")
    
    level_int = getattr(logging, level.upper())
    
    # Update root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level_int)
    
    # Update all handlers
    for handler in root_logger.handlers:
        handler.setLevel(level_int)
    
    # Reconfigure logger levels
    configure_logger_levels(level)
    
    # Log the change
    setup_logger = logging.getLogger("logging_setup")
    setup_logger.info(
        f"Log level updated to {level}",
        extra={
            'extra_data': {
                'new_level': level,
                'event_type': 'log_level_change'
            }
        }
    )


def create_logger_for_module(module_name: str) -> logging.Logger:
    """
    Create a properly configured logger for a specific module.
    
    Args:
        module_name: Name of the module
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(module_name)
    
    # Ensure logger inherits from root configuration
    logger.propagate = True
    
    return logger