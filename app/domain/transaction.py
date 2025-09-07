"""Transaction domain model representing financial transactions in the system."""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional

from .value_objects.financial_year import FinancialYear
from .value_objects.money import Money


@dataclass
class Transaction:
    """Pure domain model representing a financial transaction.

    Contains core transaction information and business rules for validation.
    """

    id: str
    partner_id: str
    amount: Money
    transaction_date: date
    financial_year: FinancialYear
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate transaction data after initialization."""
        self._validate()

    def _validate(self):
        """Validate transaction business rules."""
        if not self.id or not self.id.strip():
            raise ValueError("Transaction ID cannot be empty")

        if not self.partner_id or not self.partner_id.strip():
            raise ValueError("Partner ID cannot be empty")

        if not isinstance(self.amount, Money):
            raise ValueError("Amount must be a Money object")

        if not self.amount.is_positive():
            raise ValueError("Transaction amount must be positive")

        if not isinstance(self.transaction_date, date):
            raise ValueError("Transaction date must be a date object")

        if self.transaction_date > date.today():
            raise ValueError("Transaction date cannot be in the future")

        if not isinstance(self.financial_year, FinancialYear):
            raise ValueError("Financial year must be a FinancialYear object")

        # Validate that transaction date falls within the financial year
        if not self.financial_year.contains_date(self.transaction_date):
            raise ValueError(
                f"Transaction date {self.transaction_date} does not fall within financial year {self.financial_year}"
            )

        if self.description and len(self.description.strip()) > 500:
            raise ValueError("Description cannot exceed 500 characters")

        if self.created_at > datetime.now():
            raise ValueError("Created date cannot be in the future")

        if self.updated_at and self.updated_at < self.created_at:
            raise ValueError("Updated date cannot be before created date")

    def update_amount(self, new_amount: Money) -> "Transaction":
        """Update transaction amount with validation."""
        if not isinstance(new_amount, Money):
            raise ValueError("Amount must be a Money object")

        if not new_amount.is_positive():
            raise ValueError("Transaction amount must be positive")

        return Transaction(
            id=self.id,
            partner_id=self.partner_id,
            amount=new_amount,
            transaction_date=self.transaction_date,
            financial_year=self.financial_year,
            description=self.description,
            created_at=self.created_at,
            updated_at=datetime.now(),
        )

    def update_description(self, new_description: Optional[str]) -> "Transaction":
        """Update transaction description with validation."""
        if new_description and len(new_description.strip()) > 500:
            raise ValueError("Description cannot exceed 500 characters")

        return Transaction(
            id=self.id,
            partner_id=self.partner_id,
            amount=self.amount,
            transaction_date=self.transaction_date,
            financial_year=self.financial_year,
            description=new_description.strip() if new_description else None,
            created_at=self.created_at,
            updated_at=datetime.now(),
        )

    def update_transaction_date(self, new_date: date) -> "Transaction":
        """Update transaction date and recalculate financial year."""
        if not isinstance(new_date, date):
            raise ValueError("Transaction date must be a date object")

        if new_date > date.today():
            raise ValueError("Transaction date cannot be in the future")

        # Recalculate financial year based on new date
        new_financial_year = FinancialYear.from_date(new_date)

        return Transaction(
            id=self.id,
            partner_id=self.partner_id,
            amount=self.amount,
            transaction_date=new_date,
            financial_year=new_financial_year,
            description=self.description,
            created_at=self.created_at,
            updated_at=datetime.now(),
        )

    def get_month_name(self) -> str:
        """Get the month name of the transaction."""
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
        return months[self.transaction_date.month - 1]

    def get_year(self) -> int:
        """Get the year of the transaction."""
        return self.transaction_date.year

    def get_quarter(self) -> int:
        """Get the financial quarter (1-4) of the transaction."""
        return self.financial_year.get_quarter(self.transaction_date)

    def is_in_current_financial_year(self) -> bool:
        """Check if transaction is in the current financial year."""
        current_fy = FinancialYear.current()
        return self.financial_year == current_fy

    def get_age_in_days(self) -> int:
        """Get the age of the transaction in days."""
        return (date.today() - self.transaction_date).days

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "partner_id": self.partner_id,
            "amount": self.amount.to_float(),
            "currency": self.amount.currency,
            "transaction_date": self.transaction_date.isoformat(),
            "financial_year": self.financial_year.to_string("short"),
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        """Create Transaction from dictionary."""
        return cls(
            id=data["id"],
            partner_id=data["partner_id"],
            amount=Money.from_float(data["amount"], data.get("currency", "INR")),
            transaction_date=date.fromisoformat(data["transaction_date"]),
            financial_year=FinancialYear.from_string(data["financial_year"]),
            description=data.get("description"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=(
                datetime.fromisoformat(data["updated_at"])
                if data.get("updated_at")
                else None
            ),
        )

    def __str__(self) -> str:
        return f"Transaction(id={self.id}, partner_id={self.partner_id}, amount={self.amount}, date={self.transaction_date})"

    def __repr__(self) -> str:
        return (
            f"Transaction(id='{self.id}', partner_id='{self.partner_id}', "
            f"amount={self.amount}, transaction_date={self.transaction_date}, "
            f"financial_year={self.financial_year})"
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, Transaction):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
