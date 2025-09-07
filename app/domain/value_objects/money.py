"""Money value object for handling monetary amounts with proper validation."""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Union


@dataclass(frozen=True)
class Money:
    """Immutable value object representing a monetary amount.

    Uses Decimal for precise financial calculations and includes
    validation to ensure non-negative amounts.
    """

    amount: Decimal
    currency: str = "INR"

    def __post_init__(self):
        """Validate the money object after initialization."""
        if not isinstance(self.amount, Decimal):
            # Convert to Decimal if not already
            object.__setattr__(self, "amount", Decimal(str(self.amount)))

        if self.amount < 0:
            raise ValueError("Money amount cannot be negative")

        if not self.currency or len(self.currency) != 3:
            raise ValueError("Currency must be a 3-letter code (e.g., 'INR', 'USD')")

        # Round to 2 decimal places for currency precision
        rounded_amount = self.amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        object.__setattr__(self, "amount", rounded_amount)

    @classmethod
    def from_float(cls, amount: float, currency: str = "INR") -> "Money":
        """Create Money from float value."""
        return cls(Decimal(str(amount)), currency)

    @classmethod
    def from_int(cls, amount: int, currency: str = "INR") -> "Money":
        """Create Money from integer value."""
        return cls(Decimal(amount), currency)

    @classmethod
    def zero(cls, currency: str = "INR") -> "Money":
        """Create Money with zero amount."""
        return cls(Decimal("0"), currency)

    def add(self, other: "Money") -> "Money":
        """Add two Money objects. Must have same currency."""
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot add different currencies: {self.currency} and {other.currency}"
            )
        return Money(self.amount + other.amount, self.currency)

    def subtract(self, other: "Money") -> "Money":
        """Subtract two Money objects. Must have same currency."""
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot subtract different currencies: {self.currency} and {other.currency}"
            )
        result_amount = self.amount - other.amount
        if result_amount < 0:
            raise ValueError("Subtraction would result in negative amount")
        return Money(result_amount, self.currency)

    def multiply(self, factor: Union[int, float, Decimal]) -> "Money":
        """Multiply Money by a numeric factor."""
        if not isinstance(factor, Decimal):
            factor = Decimal(str(factor))
        if factor < 0:
            raise ValueError("Cannot multiply money by negative factor")
        return Money(self.amount * factor, self.currency)

    def divide(self, divisor: Union[int, float, Decimal]) -> "Money":
        """Divide Money by a numeric divisor."""
        if not isinstance(divisor, Decimal):
            divisor = Decimal(str(divisor))
        if divisor <= 0:
            raise ValueError("Cannot divide money by zero or negative number")
        return Money(self.amount / divisor, self.currency)

    def is_zero(self) -> bool:
        """Check if the amount is zero."""
        return self.amount == 0

    def is_positive(self) -> bool:
        """Check if the amount is positive."""
        return self.amount > 0

    def to_float(self) -> float:
        """Convert to float (use with caution for display only)."""
        return float(self.amount)

    def to_string(self, include_currency: bool = True) -> str:
        """Convert to formatted string representation."""
        if include_currency:
            return f"{self.currency} {self.amount:,.2f}"
        return f"{self.amount:,.2f}"

    def __str__(self) -> str:
        return self.to_string()

    def __repr__(self) -> str:
        return f"Money(amount={self.amount}, currency='{self.currency}')"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency

    def __lt__(self, other: "Money") -> bool:
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot compare different currencies: {self.currency} and {other.currency}"
            )
        return self.amount < other.amount

    def __le__(self, other: "Money") -> bool:
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot compare different currencies: {self.currency} and {other.currency}"
            )
        return self.amount <= other.amount

    def __gt__(self, other: "Money") -> bool:
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot compare different currencies: {self.currency} and {other.currency}"
            )
        return self.amount > other.amount

    def __ge__(self, other: "Money") -> bool:
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot compare different currencies: {self.currency} and {other.currency}"
            )
        return self.amount >= other.amount
