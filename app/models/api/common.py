"""
Common API models and utilities
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ErrorDetail(BaseModel):
    """Error detail model"""
    field: Optional[str] = Field(None, description="Field that caused the error")
    message: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")

class ErrorResponse(BaseModel):
    """Standard error response model"""
    success: bool = Field(False, description="Always false for errors")
    message: str = Field(..., description="Error message")
    details: Optional[List[ErrorDetail]] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")

class HealthCheckResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Check timestamp")
    version: Optional[str] = Field(None, description="Application version")
    database_status: Optional[str] = Field(None, description="Database connection status")
