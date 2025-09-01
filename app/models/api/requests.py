"""
Request models for API endpoints
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date
import re

class FinancialYearPath(BaseModel):
    """Path parameter for financial year"""
    financial_year: str = Field(..., description="Financial year in format FY25-26")
    
    @validator('financial_year')
    def validate_financial_year(cls, v):
        pattern = r'^FY\d{2}-\d{2}$'
        if not re.match(pattern, v):
            raise ValueError('Financial year must be in format FY25-26')
        return v

class CommissionQuery(BaseModel):
    """Query parameters for commission endpoints"""
    limit: Optional[int] = Field(10, ge=1, le=100, description="Number of items to return")
    offset: Optional[int] = Field(0, ge=0, description="Number of items to skip")
    partner_id: Optional[str] = Field(None, description="Filter by partner ID")
    financial_year: Optional[str] = Field(None, description="Filter by financial year")
    start_date: Optional[date] = Field(None, description="Filter by start date")
    end_date: Optional[date] = Field(None, description="Filter by end date")

class PartnerQuery(BaseModel):
    """Query parameters for partner endpoints"""
    limit: Optional[int] = Field(10, ge=1, le=100, description="Number of items to return")
    offset: Optional[int] = Field(0, ge=0, description="Number of items to skip")
    entity_type: Optional[str] = Field(None, description="Filter by entity type")
    search: Optional[str] = Field(None, description="Search by partner name")

class DashboardQuery(BaseModel):
    """Query parameters for dashboard endpoints"""
    financial_year: Optional[str] = Field(None, description="Financial year for metrics")
    include_trends: Optional[bool] = Field(True, description="Include trend data")
    months_back: Optional[int] = Field(6, ge=1, le=24, description="Number of months to look back")
