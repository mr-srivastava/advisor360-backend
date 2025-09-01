"""
Base models and common fields for Advisor360 application
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class EntityType(str, Enum):
    """Entity types for financial products"""
    MUTUAL_FUNDS = "Mutual Funds"
    LIFE_INSURANCE = "Life Insurance"
    HEALTH_INSURANCE = "Health Insurance"
    GENERAL_INSURANCE = "General Insurance"

class BaseResponse(BaseModel):
    """Base response model with common fields"""
    success: bool = Field(True, description="Indicates if the request was successful")
    message: Optional[str] = Field(None, description="Optional message for the response")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")

class BaseEntity(BaseModel):
    """Base entity model with common fields"""
    id: str = Field(..., description="Unique identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints"""
    limit: int = Field(10, ge=1, le=100, description="Number of items per page")
    offset: int = Field(0, ge=0, description="Number of items to skip")

class PaginatedResponse(BaseResponse):
    """Base paginated response model"""
    total: int = Field(..., description="Total number of items")
    limit: int = Field(..., description="Number of items per page")
    offset: int = Field(..., description="Number of items skipped")
    has_next: bool = Field(..., description="Whether there are more items")
    has_prev: bool = Field(..., description="Whether there are previous items")
