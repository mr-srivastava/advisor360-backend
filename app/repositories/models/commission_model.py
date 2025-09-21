"""Database model for Commission entity mapping."""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from ...domain.commission import Commission
from ...domain.value_objects.financial_year import FinancialYear
from ...domain.value_objects.money import Money


class CommissionModel(BaseModel):
    """Database model for commissions that maps between domain models and database schema.

    This model handles the conversion between the rich domain model and the
    flat database representation used by Supabase.
    """

    id: str = Field(..., description="Commission unique identifier")
    entity_id: str = Field(
        ..., description="Partner/Entity ID (maps to partner_id in domain)"
    )
    month: datetime = Field(..., description="Transaction month as datetime")
    amount: float = Field(..., ge=0, description="Commission amount as float")
    description: Optional[str] = Field(
        None, max_length=500, description="Commission description"
    )
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
        }

    def to_domain(self) -> Commission:
        """Convert database model to domain model.

        Returns:
            Commission domain model instance
        """
        # Extract date from datetime month field
        transaction_date = self.month.date()

        # Create Money value object
        money = Money.from_float(self.amount, "INR")

        # Create FinancialYear value object
        financial_year = FinancialYear.from_date(transaction_date)

        return Commission(
            id=self.id,
            partner_id=self.entity_id,
            amount=money,
            transaction_date=transaction_date,
            financial_year=financial_year,
            description=self.description,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, commission: Commission) -> "CommissionModel":
        """Create database model from domain model.

        Args:
            commission: Commission domain model

        Returns:
            CommissionModel instance
        """
        # Convert date to datetime for month field (using first day of month)
        month_datetime = datetime.combine(
            commission.transaction_date.replace(day=1), datetime.min.time()
        )

        return cls(
            id=commission.id,
            entity_id=commission.partner_id,
            month=month_datetime,
            amount=commission.amount.to_float(),
            description=commission.description,
            created_at=commission.created_at,
            updated_at=commission.updated_at,
        )

    @classmethod
    def from_database_row(cls, row: dict) -> "CommissionModel":
        """Create model from raw database row.

        Args:
            row: Raw database row dictionary

        Returns:
            CommissionModel instance
        """
        # Handle different possible datetime formats
        month_value = row.get("month")
        if isinstance(month_value, str):
            month_datetime = datetime.fromisoformat(month_value.replace("Z", "+00:00"))
        elif isinstance(month_value, datetime):
            month_datetime = month_value
        else:
            raise ValueError(f"Invalid month format: {month_value}")

        created_at_value = row.get("created_at")
        if isinstance(created_at_value, str):
            created_at = datetime.fromisoformat(created_at_value.replace("Z", "+00:00"))
        elif isinstance(created_at_value, datetime):
            created_at = created_at_value
        else:
            created_at = datetime.now()

        updated_at_value = row.get("updated_at")
        updated_at = None
        if updated_at_value:
            if isinstance(updated_at_value, str):
                updated_at = datetime.fromisoformat(
                    updated_at_value.replace("Z", "+00:00")
                )
            elif isinstance(updated_at_value, datetime):
                updated_at = updated_at_value

            # Ensure updated_at is not before created_at
            if updated_at and updated_at < created_at:
                updated_at = None  # Set to None if invalid

        return cls(
            id=row["id"],
            entity_id=row["entity_id"],
            month=month_datetime,
            amount=float(row["amount"]),
            description=row.get("description"),
            created_at=created_at,
            updated_at=updated_at,
        )

    def to_database_dict(self) -> dict:
        """Convert to dictionary for database operations.

        Returns:
            Dictionary suitable for database insertion/update
        """
        data = {
            "id": self.id,
            "entity_id": self.entity_id,
            "month": self.month.isoformat(),
            "amount": self.amount,
            "created_at": self.created_at.isoformat(),
        }

        if self.description is not None:
            data["description"] = self.description

        if self.updated_at is not None:
            data["updated_at"] = self.updated_at.isoformat()

        return data

    def get_month_name(self) -> str:
        """Get month name from the month datetime."""
        months = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
        return months[self.month.month - 1]

    def get_year(self) -> int:
        """Get year from the month datetime."""
        return self.month.year

    def get_financial_year_string(self) -> str:
        """Get financial year string representation."""
        fy = FinancialYear.from_date(self.month.date())
        return fy.to_string("short")
