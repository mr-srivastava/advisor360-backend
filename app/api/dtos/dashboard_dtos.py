"""
Dashboard DTOs for API request and response models.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime

from .common_dtos import BaseResponse, DataResponse, ListResponse

# Request DTOs
class DashboardQueryParams(BaseModel):
    """Query parameters for dashboard endpoints."""
    financial_year: Optional[str] = Field(None, description="Financial year for metrics (e.g., FY24-25)")
    include_trends: bool = Field(True, description="Include trend data")
    months_back: int = Field(6, description="Number of months to look back", ge=1, le=24)

    @validator('financial_year')
    def validate_financial_year(cls, v):
        if v is None:
            return v
        # Basic validation for FY format
        import re
        pattern = r'^FY\d{2}-\d{2}$'
        if not re.match(pattern, v):
            raise ValueError('Financial year must be in format FY24-25')
        return v

class FinancialYearPathParam(BaseModel):
    """Path parameter for financial year."""
    financial_year: str = Field(..., description="Financial year in format FY24-25")
    
    @validator('financial_year')
    def validate_financial_year(cls, v):
        import re
        pattern = r'^FY\d{2}-\d{2}$'
        if not re.match(pattern, v):
            raise ValueError('Financial year must be in format FY24-25')
        return v

# Response DTOs
class TrendData(BaseModel):
    """Trend data for statistics."""
    value: str = Field(..., description="Trend value (e.g., '+15.2%')")
    is_positive: bool = Field(..., description="Whether the trend is positive")
    percentage: float = Field(..., description="Percentage change")

class StatCard(BaseModel):
    """Individual stat card for dashboard."""
    id: str = Field(..., description="Unique identifier for the stat")
    title: str = Field(..., description="Title of the stat")
    value: str = Field(..., description="Formatted value of the stat")
    subtitle: str = Field(..., description="Subtitle or description")
    icon: str = Field(..., description="Icon identifier")
    trend: Optional[TrendData] = Field(None, description="Trend data if available")

class DashboardOverviewData(BaseModel):
    """Dashboard overview data."""
    stats: List[StatCard] = Field(..., description="List of stat cards")

class DashboardOverviewResponse(DataResponse[DashboardOverviewData]):
    """Response for dashboard overview."""
    pass
# Financial Year Metrics DTOs
class FYMetricsData(BaseModel):
    """Financial year metrics data."""
    selected_fy: str = Field(..., description="Selected financial year")
    current_year_total: float = Field(..., description="Total for current year")
    yoy_growth: float = Field(..., description="Year over year growth percentage")
    commission_count: int = Field(..., description="Number of commissions")

class FYMetricsResponse(DataResponse[FYMetricsData]):
    """Response for financial year metrics."""
    pass

# Performance Metrics DTOs
class MonthlyGrowthData(BaseModel):
    """Monthly growth data."""
    month: str = Field(..., description="Month name")
    total: float = Field(..., description="Total for the month")
    growth: Optional[float] = Field(None, description="Growth percentage")

class EntityPerformanceData(BaseModel):
    """Entity performance data."""
    entity_id: str = Field(..., description="Entity ID")
    entity_name: str = Field(..., description="Entity name")
    total: float = Field(..., description="Total amount")
    percentage: float = Field(..., description="Percentage of total")

class PerformanceMetricsData(BaseModel):
    """Performance metrics data."""
    monthly_growth: List[MonthlyGrowthData] = Field(..., description="Monthly growth data")
    entity_performance: List[EntityPerformanceData] = Field(..., description="Entity performance data")

class PerformanceMetricsResponse(DataResponse[PerformanceMetricsData]):
    """Response for performance metrics."""
    pass

# Recent Activities DTOs
class RecentCommissionActivity(BaseModel):
    """Recent commission activity data."""
    id: str = Field(..., description="Commission ID")
    partner_name: str = Field(..., description="Partner name")
    amount: float = Field(..., description="Commission amount")
    currency: str = Field(..., description="Currency code")
    date: datetime = Field(..., description="Transaction date")
    financial_year: str = Field(..., description="Financial year")

class MonthlyCommissionSummary(BaseModel):
    """Monthly commission summary data."""
    month: str = Field(..., description="Month name")
    year: int = Field(..., description="Year")
    total: float = Field(..., description="Total amount")
    count: int = Field(..., description="Number of commissions")

class RecentActivityData(BaseModel):
    """Recent activity data."""
    recent_commissions: List[RecentCommissionActivity] = Field(..., description="Recent commission records")
    monthly_commissions: List[MonthlyCommissionSummary] = Field(..., description="Monthly commission summaries")

class RecentActivityResponse(DataResponse[RecentActivityData]):
    """Response for recent activities."""
    pass

# Financial Years DTOs
class FinancialYearsData(BaseModel):
    """Financial years data."""
    financial_years: List[str] = Field(..., description="List of available financial years")

class FinancialYearsResponse(DataResponse[FinancialYearsData]):
    """Response for available financial years."""
    pass

# Analytics DTOs
class QuarterlyData(BaseModel):
    """Quarterly performance data."""
    quarter: int = Field(..., description="Quarter number (1-4)")
    quarter_name: str = Field(..., description="Quarter name (Q1, Q2, etc.)")
    total: float = Field(..., description="Total amount for the quarter")
    count: int = Field(..., description="Number of transactions")
    growth: Optional[float] = Field(None, description="Growth compared to previous quarter")

class YearlyComparisonData(BaseModel):
    """Yearly comparison data."""
    financial_year: str = Field(..., description="Financial year")
    total: float = Field(..., description="Total amount")
    count: int = Field(..., description="Number of transactions")
    growth: Optional[float] = Field(None, description="Growth compared to previous year")

class DashboardAnalyticsData(BaseModel):
    """Comprehensive dashboard analytics data."""
    quarterly_data: List[QuarterlyData] = Field(..., description="Quarterly breakdown")
    yearly_comparison: List[YearlyComparisonData] = Field(..., description="Year-over-year comparison")
    top_performers: List[EntityPerformanceData] = Field(..., description="Top performing entities")

class DashboardAnalyticsResponse(DataResponse[DashboardAnalyticsData]):
    """Response for dashboard analytics."""
    pass

# Mapping utilities
class DashboardMapper:
    """Utility class for mapping dashboard data."""
    
    @staticmethod
    def create_stat_card(
        id: str, 
        title: str, 
        value: str, 
        subtitle: str, 
        icon: str,
        trend: Optional[TrendData] = None
    ) -> StatCard:
        """Create a stat card."""
        return StatCard(
            id=id,
            title=title,
            value=value,
            subtitle=subtitle,
            icon=icon,
            trend=trend
        )
    
    @staticmethod
    def create_trend_data(percentage: float) -> TrendData:
        """Create trend data from percentage."""
        is_positive = percentage >= 0
        sign = "+" if is_positive else ""
        
        return TrendData(
            value=f"{sign}{percentage:.1f}%",
            is_positive=is_positive,
            percentage=percentage
        )
    
    @staticmethod
    def format_currency(amount: float, currency: str = "INR") -> str:
        """Format currency amount for display."""
        if amount >= 10000000:  # 1 crore
            return f"₹{amount/10000000:.1f}Cr"
        elif amount >= 100000:  # 1 lakh
            return f"₹{amount/100000:.1f}L"
        elif amount >= 1000:  # 1 thousand
            return f"₹{amount/1000:.1f}K"
        else:
            return f"₹{amount:.0f}"