"""
Application Configuration Management

Centralized configuration with environment variable loading and validation.
Supports environment-specific configurations and proper configuration validation.
"""

import os
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseModel):
    """Database configuration settings"""
    url: str = Field(..., description="Supabase database URL")
    key: str = Field(..., description="Supabase API key")
    timeout: int = Field(default=30, description="Database connection timeout in seconds")
    
    @validator('url')
    def validate_url(cls, v):
        if not v or not v.startswith(('http://', 'https://')):
            raise ValueError('Database URL must be a valid HTTP/HTTPS URL')
        return v
    
    @validator('key')
    def validate_key(cls, v):
        if not v or len(v) < 10:
            raise ValueError('Database key must be at least 10 characters long')
        return v
    
    @validator('timeout')
    def validate_timeout(cls, v):
        if v <= 0:
            raise ValueError('Timeout must be greater than 0')
        return v


class CORSConfig(BaseModel):
    """CORS configuration settings"""
    origins: List[str] = Field(default_factory=lambda: ["*"], description="Allowed CORS origins")
    methods: List[str] = Field(default_factory=lambda: ["*"], description="Allowed HTTP methods")
    headers: List[str] = Field(default_factory=lambda: ["*"], description="Allowed headers")
    credentials: bool = Field(default=True, description="Allow credentials in CORS requests")


class LoggingConfig(BaseModel):
    """Logging configuration settings"""
    level: str = Field(default="INFO", description="Logging level")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format"
    )
    file_path: Optional[str] = Field(default=None, description="Log file path (optional)")
    max_file_size: int = Field(default=10485760, description="Max log file size in bytes (10MB)")
    backup_count: int = Field(default=5, description="Number of backup log files to keep")
    
    @validator('level')
    def validate_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of: {valid_levels}')
        return v.upper()


class AppConfig(BaseSettings):
    """
    Main application configuration
    
    Loads configuration from environment variables with proper validation
    and default values.
    """
    
    # Application settings
    app_name: str = Field(default="Commission Tracker API", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    environment: str = Field(default="development", description="Environment (development, staging, production)")
    
    # Server settings
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    
    # Database configuration
    database_url: str = Field(..., description="Supabase database URL")
    database_key: str = Field(..., description="Supabase API key")
    database_timeout: int = Field(default=30, env="DATABASE_TIMEOUT", description="Database timeout")
    
    # CORS settings
    cors_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:8080"],
        env="CORS_ORIGINS",
        description="Allowed CORS origins"
    )
    
    # Logging settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL", description="Logging level")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE", description="Log file path")
    
    # Security settings
    secret_key: str = Field(default="dev-secret-key", env="SECRET_KEY", description="Secret key for security")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }
        
    @validator('environment')
    def validate_environment(cls, v):
        valid_envs = ['development', 'staging', 'production']
        if v.lower() not in valid_envs:
            raise ValueError(f'Environment must be one of: {valid_envs}')
        return v.lower()
    
    @validator('port')
    def validate_port(cls, v):
        if not (1 <= v <= 65535):
            raise ValueError('Port must be between 1 and 65535')
        return v
    
    @validator('cors_origins', pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
    
    @property
    def database(self) -> DatabaseConfig:
        """Get database configuration"""
        return DatabaseConfig(
            url=self.database_url,
            key=self.database_key,
            timeout=self.database_timeout
        )
    
    @property
    def cors(self) -> CORSConfig:
        """Get CORS configuration"""
        return CORSConfig(origins=self.cors_origins)
    
    @property
    def logging(self) -> LoggingConfig:
        """Get logging configuration"""
        return LoggingConfig(
            level=self.log_level,
            file_path=self.log_file
        )
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.environment == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.environment == "production"


# Global configuration instance
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """
    Get the global configuration instance
    
    Returns:
        AppConfig: The application configuration
    """
    global _config
    if _config is None:
        _config = AppConfig()
    return _config


def set_config(config: AppConfig) -> None:
    """
    Set the global configuration instance (useful for testing)
    
    Args:
        config: The configuration instance to set
    """
    global _config
    _config = config


def load_config_from_env() -> AppConfig:
    """
    Load configuration from environment variables
    
    Returns:
        AppConfig: Loaded and validated configuration
    """
    return AppConfig()


def validate_config(config: AppConfig) -> None:
    """
    Validate configuration at startup
    
    Args:
        config: Configuration to validate
        
    Raises:
        ValueError: If configuration is invalid
    """
    # Validate database connection settings
    if not config.database_url or not config.database_key:
        raise ValueError("Database URL and key are required")
    
    # Validate environment-specific settings
    if config.is_production and config.secret_key == "dev-secret-key":
        raise ValueError("Production environment requires a proper secret key")
    
    # Additional validation can be added here
    print(f"Configuration validated successfully for environment: {config.environment}")