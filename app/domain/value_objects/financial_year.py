"""FinancialYear value object for handling financial year calculations and validation."""

import re
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class FinancialYear:
    """Immutable value object representing a financial year.

    Handles Indian financial year format (April to March) and provides
    utilities for date calculations and validation.
    """

    start_year: int
    end_year: int

    def __post_init__(self):
        """Validate the financial year after initialization."""
        if self.end_year != self.start_year + 1:
            raise ValueError(
                f"Invalid financial year: end year must be start year + 1. Got {self.start_year}-{self.end_year}"
            )

        if self.start_year < 1900 or self.start_year > 2100:
            raise ValueError(
                f"Financial year start year must be between 1900 and 2100. Got {self.start_year}"
            )

    @classmethod
    def from_string(cls, fy_string: str) -> "FinancialYear":
        """Create FinancialYear from string format.

        Supports formats:
        - "FY24-25", "FY2024-25", "FY2024-2025"
        - "2024-25", "2024-2025"
        - "24-25"
        """
        if not fy_string:
            raise ValueError("Financial year string cannot be empty")

        # Remove FY prefix if present
        clean_string = fy_string.upper().replace("FY", "").strip()

        # Pattern to match various formats
        patterns = [
            r"^(\d{4})-(\d{4})$",  # 2024-2025
            r"^(\d{4})-(\d{2})$",  # 2024-25
            r"^(\d{2})-(\d{2})$",  # 24-25
        ]

        for pattern in patterns:
            match = re.match(pattern, clean_string)
            if match:
                start_str, end_str = match.groups()

                # Handle 2-digit years
                if len(start_str) == 2:
                    start_year = 2000 + int(start_str)
                else:
                    start_year = int(start_str)

                if len(end_str) == 2:
                    # For 2-digit end year, determine century based on start year
                    end_year_suffix = int(end_str)
                    if end_year_suffix == (start_year + 1) % 100:
                        end_year = start_year + 1
                    else:
                        # Handle century boundary cases
                        if start_year % 100 == 99:
                            end_year = start_year + 1
                        else:
                            end_year = (start_year // 100) * 100 + end_year_suffix
                else:
                    end_year = int(end_str)

                return cls(start_year, end_year)

        raise ValueError(
            f"Invalid financial year format: {fy_string}. Expected formats: FY24-25, 2024-25, or 2024-2025"
        )

    @classmethod
    def from_date(cls, date_obj: date) -> "FinancialYear":
        """Create FinancialYear from a date object."""
        if date_obj.month >= 4:  # April to March
            return cls(date_obj.year, date_obj.year + 1)
        else:
            return cls(date_obj.year - 1, date_obj.year)

    @classmethod
    def current(cls) -> "FinancialYear":
        """Get the current financial year based on today's date."""
        return cls.from_date(date.today())

    @classmethod
    def from_year(cls, year: int) -> "FinancialYear":
        """Create FinancialYear starting from the given year."""
        return cls(year, year + 1)

    def get_start_date(self) -> date:
        """Get the start date of the financial year (April 1st)."""
        return date(self.start_year, 4, 1)

    def get_end_date(self) -> date:
        """Get the end date of the financial year (March 31st)."""
        return date(self.end_year, 3, 31)

    def contains_date(self, date_obj: date) -> bool:
        """Check if a date falls within this financial year."""
        return self.get_start_date() <= date_obj <= self.get_end_date()

    def contains_month(self, year: int, month: int) -> bool:
        """Check if a specific month/year falls within this financial year."""
        check_date = date(year, month, 1)
        return self.contains_date(check_date)

    def get_months(self) -> list[tuple[int, int]]:
        """Get all months in this financial year as (year, month) tuples."""
        months = []

        # April to December of start year
        for month in range(4, 13):
            months.append((self.start_year, month))

        # January to March of end year
        for month in range(1, 4):
            months.append((self.end_year, month))

        return months

    def get_quarter(self, date_obj: date) -> int:
        """Get the quarter (1-4) for a date within this financial year."""
        if not self.contains_date(date_obj):
            raise ValueError(f"Date {date_obj} is not within financial year {self}")

        if date_obj.month >= 4 and date_obj.month <= 6:
            return 1  # Q1: Apr-Jun
        elif date_obj.month >= 7 and date_obj.month <= 9:
            return 2  # Q2: Jul-Sep
        elif date_obj.month >= 10 and date_obj.month <= 12:
            return 3  # Q3: Oct-Dec
        else:  # Jan-Mar
            return 4  # Q4: Jan-Mar

    def next_year(self) -> "FinancialYear":
        """Get the next financial year."""
        return FinancialYear(self.start_year + 1, self.end_year + 1)

    def previous_year(self) -> "FinancialYear":
        """Get the previous financial year."""
        return FinancialYear(self.start_year - 1, self.end_year - 1)

    def to_string(self, format_type: str = "short") -> str:
        """Convert to string representation.

        Args:
            format_type: "short" (FY24-25), "medium" (FY2024-25), or "long" (FY2024-2025)
        """
        if format_type == "short":
            return f"FY{self.start_year % 100:02d}-{self.end_year % 100:02d}"
        elif format_type == "medium":
            return f"FY{self.start_year}-{self.end_year % 100:02d}"
        elif format_type == "long":
            return f"FY{self.start_year}-{self.end_year}"
        else:
            raise ValueError(
                f"Invalid format_type: {format_type}. Use 'short', 'medium', or 'long'"
            )

    def __str__(self) -> str:
        return self.to_string("short")

    def __repr__(self) -> str:
        return f"FinancialYear(start_year={self.start_year}, end_year={self.end_year})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, FinancialYear):
            return False
        return self.start_year == other.start_year and self.end_year == other.end_year

    def __lt__(self, other: "FinancialYear") -> bool:
        return self.start_year < other.start_year

    def __le__(self, other: "FinancialYear") -> bool:
        return self.start_year <= other.start_year

    def __gt__(self, other: "FinancialYear") -> bool:
        return self.start_year > other.start_year

    def __ge__(self, other: "FinancialYear") -> bool:
        return self.start_year >= other.start_year
