"""
Database Configuration

Specific database configuration utilities and connection management settings.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
import os


class ConnectionPoolConfig(BaseModel):
    """Database connection pool configuration"""
    min_connections: int = Field(default=1, description="Minimum number of connections in pool")
    max_connections: int = Field(default=10, description="Maximum number of connections in pool")
    connection_timeout: int = Field(default=30, description="Connection timeout in seconds")
    idle_timeout: int = Field(default=300, description="Idle connection timeout in seconds")
    
    @validator('min_connections')
    def validate_min_connections(cls, v):
        if v < 1:
            raise ValueError('Minimum connections must be at least 1')
        return v
    
    @validator('max_connections')
    def validate_max_connections(cls, v):
        if v < 1:
            raise ValueError('Maximum connections must be at least 1')
        return v
    
    @validator('max_connections')
    def validate_max_greater_than_min(cls, v, values):
        if 'min_connections' in values and v < values['min_connections']:
            raise ValueError('Maximum connections must be greater than or equal to minimum connections')
        return v


class RetryConfig(BaseModel):
    """Database retry configuration"""
    max_retries: int = Field(default=3, description="Maximum number of retry attempts")
    retry_delay: float = Field(default=1.0, description="Delay between retries in seconds")
    exponential_backoff: bool = Field(default=True, description="Use exponential backoff for retries")
    max_retry_delay: float = Field(default=60.0, description="Maximum retry delay in seconds")
    
    @validator('max_retries')
    def validate_max_retries(cls, v):
        if v < 0:
            raise ValueError('Maximum retries cannot be negative')
        return v
    
    @validator('retry_delay')
    def validate_retry_delay(cls, v):
        if v < 0:
            raise ValueError('Retry delay cannot be negative')
        return v


class DatabaseConfig(BaseModel):
    """
    Comprehensive database configuration
    
    Includes connection settings, pool configuration, and retry policies.
    """
    
    # Connection settings
    url: str = Field(..., description="Database connection URL")
    key: str = Field(..., description="Database API key")
    timeout: int = Field(default=30, description="Query timeout in seconds")
    
    # Pool configuration
    pool: ConnectionPoolConfig = Field(default_factory=ConnectionPoolConfig)
    
    # Retry configuration
    retry: RetryConfig = Field(default_factory=RetryConfig)
    
    # Additional settings
    enable_logging: bool = Field(default=False, description="Enable database query logging")
    log_slow_queries: bool = Field(default=True, description="Log slow queries")
    slow_query_threshold: float = Field(default=1.0, description="Slow query threshold in seconds")
    
    # SSL and security settings
    ssl_mode: str = Field(default="require", description="SSL mode for connections")
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")
    
    @validator('url')
    def validate_url(cls, v):
        if not v:
            raise ValueError('Database URL is required')
        if not v.startswith(('http://', 'https://', 'postgresql://', 'postgres://')):
            raise ValueError('Database URL must be a valid URL')
        return v
    
    @validator('key')
    def validate_key(cls, v):
        if not v:
            raise ValueError('Database key is required')
        if len(v) < 10:
            raise ValueError('Database key must be at least 10 characters long')
        return v
    
    @validator('timeout')
    def validate_timeout(cls, v):
        if v <= 0:
            raise ValueError('Timeout must be greater than 0')
        return v
    
    @validator('ssl_mode')
    def validate_ssl_mode(cls, v):
        valid_modes = ['disable', 'allow', 'prefer', 'require', 'verify-ca', 'verify-full']
        if v not in valid_modes:
            raise ValueError(f'SSL mode must be one of: {valid_modes}')
        return v
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """
        Create database configuration from environment variables
        
        Returns:
            DatabaseConfig: Configuration loaded from environment
        """
        return cls(
            url=os.getenv('SUPABASE_URL', ''),
            key=os.getenv('SUPABASE_KEY', ''),
            timeout=int(os.getenv('DATABASE_TIMEOUT', '30')),
            enable_logging=os.getenv('DATABASE_LOGGING', 'false').lower() == 'true',
            log_slow_queries=os.getenv('LOG_SLOW_QUERIES', 'true').lower() == 'true',
            slow_query_threshold=float(os.getenv('SLOW_QUERY_THRESHOLD', '1.0')),
            ssl_mode=os.getenv('DATABASE_SSL_MODE', 'require'),
            verify_ssl=os.getenv('DATABASE_VERIFY_SSL', 'true').lower() == 'true'
        )
    
    def get_connection_params(self) -> Dict[str, Any]:
        """
        Get connection parameters for database client
        
        Returns:
            Dict[str, Any]: Connection parameters
        """
        return {
            'url': self.url,
            'key': self.key,
            'timeout': self.timeout,
            'verify_ssl': self.verify_ssl
        }
    
    def get_pool_params(self) -> Dict[str, Any]:
        """
        Get connection pool parameters
        
        Returns:
            Dict[str, Any]: Pool parameters
        """
        return {
            'min_size': self.pool.min_connections,
            'max_size': self.pool.max_connections,
            'timeout': self.pool.connection_timeout,
            'idle_timeout': self.pool.idle_timeout
        }
    
    def should_log_query(self, execution_time: float) -> bool:
        """
        Determine if a query should be logged based on execution time
        
        Args:
            execution_time: Query execution time in seconds
            
        Returns:
            bool: True if query should be logged
        """
        if not self.enable_logging:
            return False
        
        if self.log_slow_queries and execution_time >= self.slow_query_threshold:
            return True
        
        return self.enable_logging