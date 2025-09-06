"""
Commission DTOs for API request and response models.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal

from .common_dtos import BaseResponse, DataResponse, ListResponse, PaginatedResponse
from app.domain.commission import Commission
from app.domain.partner import Partner
from app.domain.value_objects.money import Money
from app.domain.value_objects.financial_year import FinancialYear

# Request DTOs
class CreateCommissionRequest(BaseModel):
    """Request model for creating a new commission."""
    partner_id: str = Field(..., description="ID of the partner", min_length=1)
    amount: float = Field(..., description="Commission amount", gt=0)
    currency: str = Field("INR", description="Currency code", min_length=3, max_length=3)
    transaction_date: date = Field(..., description="Date of the transaction")
    description: Optional[str] = Field(None, description="Optional description", max_length=500)

    @validator('transaction_date')
    def validate_transaction_date(cls, v):
        if v > date.today():
            raise ValueError('Transaction date cannot be in the future')
        return v

    @validator('currency')
    def validate_currency(cls, v):
        return v.upper()

    def to_domain(self) -> Commission:
        """Convert to domain model."""
        money = Money.from_float(self.amount, self.currency)
        return Commission.create_new(
            partner_id=self.partner_id,
            amount=money,
            transaction_date=self.transaction_date,
            description=self.description
        )

class UpdateCommissionRequest(BaseModel):
    """Request model for updating an existing commission."""
    amount: Optional[float] = Field(None, description="Commission amount", gt=0)
    currency: Optional[str] = Field(None, description="Currency code", min_length=3, max_length=3)
    transaction_date: Optional[date] = Field(None, description="Date of the transaction")
    description: Optional[str] = Field(None, description="Optional description", max_length=500)

    @validator('transaction_date')
    def validate_transaction_date(cls, v):
        if v and v > date.today():
            raise ValueError('Transaction date cannot be in the future')
        return v

    @validator('currency')
    def validate_currency(cls, v):
        return v.upper() if v else v

class CommissionQueryParams(BaseModel):
    """Query parameters for commission endpoints."""
    partner_id: Optional[str] = Field(None, description="Filter by partner ID")
    financial_year: Optional[str] = Field(None, description="Filter by financial year (e.g., FY24-25)")
    start_date: Optional[date] = Field(None, description="Filter by start date")
    end_date: Optional[date] = Field(None, description="Filter by end date")
    min_amount: Optional[float] = Field(None, description="Minimum amount filter", ge=0)
    max_amount: Optional[float] = Field(None, description="Maximum amount filter", ge=0)
    page: int = Field(1, description="Page number", ge=1)
    per_page: int = Field(10, description="Items per page", ge=1, le=100)

    @validator('end_date')
    def validate_date_range(cls, v, values):
        if v and 'start_date' in values and values['start_date']:
            if v < values['start_date']:
                raise ValueError('End date must be after start date')
        return v

    @validator('max_amount')
    def validate_amount_range(cls, v, values):
        if v and 'min_amount' in values and values['min_amount']:
            if v < values['min_amount']:
                raise ValueError('Max amount must be greater than min amount')
        return v

# Response DTOs
class CommissionResponse(BaseModel):
    """Response model for commission data."""
    id: str = Field(..., description="Commission ID")
    partner_id: str = Field(..., description="Partner ID")
    partner_name: Optional[str] = Field(None, description="Partner name")
    partner_entity_type: Optional[str] = Field(None, description="Partner entity type")
    amount: float = Field(..., description="Commission amount")
    currency: str = Field(..., description="Currency code")
    transaction_date: date = Field(..., description="Transaction date")
    month: str = Field(..., description="Month name")
    year: int = Field(..., description="Year")
    financial_year: str = Field(..., description="Financial year")
    quarter: int = Field(..., description="Financial quarter (1-4)")
    description: Optional[str] = Field(None, description="Commission description")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    @classmethod
    def from_domain(cls, commission: Commission, partner: Optional[Partner] = None) -> "CommissionResponse":
        """Create response DTO from domain model."""
        return cls(
            id=commission.id,
            partner_id=commission.partner_id,
            partner_name=partner.name if partner else None,
            partner_entity_type=partner.entity_type.value if partner else None,
            amount=commission.amount.to_float(),
            currency=commission.amount.currency,
            transaction_date=commission.transaction_date,
            month=commission.get_month_name(),
            year=commission.get_year(),
            financial_year=commission.financial_year.to_string("short"),
            quarter=commission.get_quarter(),
            description=commission.description,
            created_at=commission.created_at,
            updated_at=commission.updated_at
        )

class CommissionSummary(BaseModel):
    """Summary information for commission aggregations."""
    total_amount: float = Field(..., description="Total commission amount")
    currency: str = Field(..., description="Currency code")
    count: int = Field(..., description="Number of commissions")
    average_amount: float = Field(..., description="Average commission amount")
    financial_year: str = Field(..., description="Financial year")

class CommissionDetailResponse(DataResponse[CommissionResponse]):
    """Response for single commission detail."""
    pass

class CommissionListResponse(ListResponse[CommissionResponse]):
    """Response for commission list."""
    summary: Optional[CommissionSummary] = Field(None, description="Summary statistics")

class CommissionPaginatedResponse(PaginatedResponse[CommissionResponse]):
    """Paginated response for commission list."""
    summary: Optional[CommissionSummary] = Field(None, description="Summary statistics")

# Analytics DTOs
class MonthlyCommissionData(BaseModel):
    """Monthly commission aggregation data."""
    month: str = Field(..., description="Month name")
    year: int = Field(..., description="Year")
    total_amount: float = Field(..., description="Total amount for the month")
    count: int = Field(..., description="Number of commissions")
    growth_percentage: Optional[float] = Field(None, description="Growth compared to previous month")

class PartnerCommissionData(BaseModel):
    """Partner-wise commission aggregation data."""
    partner_id: str = Field(..., description="Partner ID")
    partner_name: str = Field(..., description="Partner name")
    entity_type: str = Field(..., description="Entity type")
    total_amount: float = Field(..., description="Total commission amount")
    count: int = Field(..., description="Number of commissions")
    percentage_of_total: float = Field(..., description="Percentage of total commissions")

class CommissionAnalyticsResponse(BaseResponse):
    """Response for commission analytics."""
    monthly_data: List[MonthlyCommissionData] = Field(..., description="Monthly breakdown")
    partner_data: List[PartnerCommissionData] = Field(..., description="Partner-wise breakdown")
    total_summary: CommissionSummary = Field(..., description="Overall summary")

# Mapping utilities
class CommissionMapper:
    """Utility class for mapping between domain models and DTOs."""
    
    @staticmethod
    def to_response(commission: Commission, partner: Optional[Partner] = None) -> CommissionResponse:
        """Convert domain model to response DTO."""
        return CommissionResponse.from_domain(commission, partner)
    
    @staticmethod
    def to_response_list(commissions: List[Commission], partners: Optional[List[Partner]] = None) -> List[CommissionResponse]:
        """Convert list of domain models to response DTOs."""
        partner_map = {p.id: p for p in partners} if partners else {}
        return [
            CommissionResponse.from_domain(commission, partner_map.get(commission.partner_id))
            for commission in commissions
        ]
    
    @staticmethod
    def create_summary(commissions: List[Commission], financial_year: Optional[str] = None) -> CommissionSummary:
        """Create summary from list of commissions."""
        if not commissions:
            return CommissionSummary(
                total_amount=0.0,
                currency="INR",
                count=0,
                average_amount=0.0,
                financial_year=financial_year or "N/A"
            )
        
        total = sum(c.amount.to_float() for c in commissions)
        count = len(commissions)
        currency = commissions[0].amount.currency
        
        return CommissionSummary(
            total_amount=total,
            currency=currency,
            count=count,
            average_amount=total / count if count > 0 else 0.0,
            financial_year=financial_year or commissions[0].financial_year.to_string("short")
        )