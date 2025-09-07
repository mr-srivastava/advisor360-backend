"""Transaction DTOs for API request and response models."""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, validator

from app.domain.partner import Partner
from app.domain.transaction import Transaction
from app.domain.value_objects.financial_year import FinancialYear
from app.domain.value_objects.money import Money

from .common_dtos import BaseResponse, DataResponse, ListResponse, PaginatedResponse


# Request DTOs
class CreateTransactionRequest(BaseModel):
    """Request model for creating a new transaction."""

    partner_id: str = Field(..., description="ID of the partner", min_length=1)
    amount: float = Field(..., description="Transaction amount", gt=0)
    currency: str = Field(
        "INR", description="Currency code", min_length=3, max_length=3
    )
    transaction_date: date = Field(..., description="Date of the transaction")
    description: Optional[str] = Field(
        None, description="Optional description", max_length=500
    )

    @validator("transaction_date")
    def validate_transaction_date(cls, v):
        if v > date.today():
            raise ValueError("Transaction date cannot be in the future")
        return v

    @validator("currency")
    def validate_currency(cls, v):
        return v.upper()

    def to_domain(self, transaction_id: str) -> Transaction:
        """Convert to domain model."""
        money = Money.from_float(self.amount, self.currency)
        financial_year = FinancialYear.from_date(self.transaction_date)

        return Transaction(
            id=transaction_id,
            partner_id=self.partner_id,
            amount=money,
            transaction_date=self.transaction_date,
            financial_year=financial_year,
            description=self.description,
        )


class UpdateTransactionRequest(BaseModel):
    """Request model for updating an existing transaction."""

    amount: Optional[float] = Field(None, description="Transaction amount", gt=0)
    currency: Optional[str] = Field(
        None, description="Currency code", min_length=3, max_length=3
    )
    transaction_date: Optional[date] = Field(
        None, description="Date of the transaction"
    )
    description: Optional[str] = Field(
        None, description="Optional description", max_length=500
    )

    @validator("transaction_date")
    def validate_transaction_date(cls, v):
        if v and v > date.today():
            raise ValueError("Transaction date cannot be in the future")
        return v

    @validator("currency")
    def validate_currency(cls, v):
        return v.upper() if v else v


class TransactionQueryParams(BaseModel):
    """Query parameters for transaction endpoints."""

    partner_id: Optional[str] = Field(None, description="Filter by partner ID")
    financial_year: Optional[str] = Field(
        None, description="Filter by financial year (e.g., FY24-25)"
    )
    start_date: Optional[date] = Field(None, description="Filter by start date")
    end_date: Optional[date] = Field(None, description="Filter by end date")
    min_amount: Optional[float] = Field(None, description="Minimum amount filter", ge=0)
    max_amount: Optional[float] = Field(None, description="Maximum amount filter", ge=0)
    page: int = Field(1, description="Page number", ge=1)
    per_page: int = Field(10, description="Items per page", ge=1, le=100)

    @validator("end_date")
    def validate_date_range(cls, v, values):
        if v and "start_date" in values and values["start_date"]:
            if v < values["start_date"]:
                raise ValueError("End date must be after start date")
        return v

    @validator("max_amount")
    def validate_amount_range(cls, v, values):
        if v and "min_amount" in values and values["min_amount"]:
            if v < values["min_amount"]:
                raise ValueError("Max amount must be greater than min amount")
        return v


# Response DTOs
class TransactionResponse(BaseModel):
    """Response model for transaction data."""

    id: str = Field(..., description="Transaction ID")
    partner_id: str = Field(..., description="Partner ID")
    partner_name: Optional[str] = Field(None, description="Partner name")
    partner_entity_type: Optional[str] = Field(None, description="Partner entity type")
    amount: float = Field(..., description="Transaction amount")
    currency: str = Field(..., description="Currency code")
    transaction_date: date = Field(..., description="Transaction date")
    month: str = Field(..., description="Month name")
    year: int = Field(..., description="Year")
    financial_year: str = Field(..., description="Financial year")
    quarter: int = Field(..., description="Financial quarter (1-4)")
    description: Optional[str] = Field(None, description="Transaction description")
    age_in_days: int = Field(..., description="Age of transaction in days")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    @classmethod
    def from_domain(
        cls, transaction: Transaction, partner: Optional[Partner] = None
    ) -> "TransactionResponse":
        """Create response DTO from domain model."""
        return cls(
            id=transaction.id,
            partner_id=transaction.partner_id,
            partner_name=partner.name if partner else None,
            partner_entity_type=partner.entity_type.value if partner else None,
            amount=transaction.amount.to_float(),
            currency=transaction.amount.currency,
            transaction_date=transaction.transaction_date,
            month=transaction.get_month_name(),
            year=transaction.get_year(),
            financial_year=transaction.financial_year.to_string("short"),
            quarter=transaction.get_quarter(),
            description=transaction.description,
            age_in_days=transaction.get_age_in_days(),
            created_at=transaction.created_at,
            updated_at=transaction.updated_at,
        )


class TransactionSummary(BaseModel):
    """Summary information for transaction aggregations."""

    total_amount: float = Field(..., description="Total transaction amount")
    currency: str = Field(..., description="Currency code")
    count: int = Field(..., description="Number of transactions")
    average_amount: float = Field(..., description="Average transaction amount")
    financial_year: str = Field(..., description="Financial year")


class TransactionDetailResponse(DataResponse[TransactionResponse]):
    """Response for single transaction detail."""

    pass


class TransactionListResponse(ListResponse[TransactionResponse]):
    """Response for transaction list."""

    summary: Optional[TransactionSummary] = Field(
        None, description="Summary statistics"
    )


class TransactionPaginatedResponse(PaginatedResponse[TransactionResponse]):
    """Paginated response for transaction list."""

    summary: Optional[TransactionSummary] = Field(
        None, description="Summary statistics"
    )


# Analytics DTOs
class MonthlyTransactionData(BaseModel):
    """Monthly transaction aggregation data."""

    month: str = Field(..., description="Month name")
    year: int = Field(..., description="Year")
    total_amount: float = Field(..., description="Total amount for the month")
    count: int = Field(..., description="Number of transactions")
    average_amount: float = Field(..., description="Average transaction amount")


class PartnerTransactionData(BaseModel):
    """Partner-wise transaction aggregation data."""

    partner_id: str = Field(..., description="Partner ID")
    partner_name: str = Field(..., description="Partner name")
    entity_type: str = Field(..., description="Entity type")
    total_amount: float = Field(..., description="Total transaction amount")
    count: int = Field(..., description="Number of transactions")
    percentage_of_total: float = Field(
        ..., description="Percentage of total transactions"
    )


class TransactionAnalyticsResponse(BaseResponse):
    """Response for transaction analytics."""

    monthly_data: list[MonthlyTransactionData] = Field(
        ..., description="Monthly breakdown"
    )
    partner_data: list[PartnerTransactionData] = Field(
        ..., description="Partner-wise breakdown"
    )
    total_summary: TransactionSummary = Field(..., description="Overall summary")


# Mapping utilities
class TransactionMapper:
    """Utility class for mapping between domain models and DTOs."""

    @staticmethod
    def to_response(
        transaction: Transaction, partner: Optional[Partner] = None
    ) -> TransactionResponse:
        """Convert domain model to response DTO."""
        return TransactionResponse.from_domain(transaction, partner)

    @staticmethod
    def to_response_list(
        transactions: list[Transaction], partners: Optional[list[Partner]] = None
    ) -> list[TransactionResponse]:
        """Convert list of domain models to response DTOs."""
        partner_map = {p.id: p for p in partners} if partners else {}
        return [
            TransactionResponse.from_domain(
                transaction, partner_map.get(transaction.partner_id)
            )
            for transaction in transactions
        ]

    @staticmethod
    def create_summary(
        transactions: list[Transaction], financial_year: Optional[str] = None
    ) -> TransactionSummary:
        """Create summary from list of transactions."""
        if not transactions:
            return TransactionSummary(
                total_amount=0.0,
                currency="INR",
                count=0,
                average_amount=0.0,
                financial_year=financial_year or "N/A",
            )

        total = sum(t.amount.to_float() for t in transactions)
        count = len(transactions)
        currency = transactions[0].amount.currency

        return TransactionSummary(
            total_amount=total,
            currency=currency,
            count=count,
            average_amount=total / count if count > 0 else 0.0,
            financial_year=financial_year
            or transactions[0].financial_year.to_string("short"),
        )
