"""Custom exceptions for Advisor360 application."""


class Advisor360Exception(Exception):
    """Base exception for Advisor360 application."""

    pass


class FinancialYearNotFound(Advisor360Exception):
    """Raised when a financial year is not found."""

    def __init__(self, financial_year: str):
        self.financial_year = financial_year
        super().__init__(f"Financial year {financial_year} not found")


class PartnerNotFound(Advisor360Exception):
    """Raised when a partner/entity is not found."""

    def __init__(self, partner_id: str):
        self.partner_id = partner_id
        super().__init__(f"Partner with ID {partner_id} not found")


class CommissionNotFound(Advisor360Exception):
    """Raised when a commission record is not found."""

    def __init__(self, commission_id: str):
        self.commission_id = commission_id
        super().__init__(f"Commission with ID {commission_id} not found")


class InvalidFinancialYearFormat(Advisor360Exception):
    """Raised when financial year format is invalid."""

    def __init__(self, financial_year: str):
        self.financial_year = financial_year
        super().__init__(
            f"Invalid financial year format: {financial_year}. Expected format: FY25-26"
        )


class DatabaseError(Advisor360Exception):
    """Raised when database operations fail."""

    def __init__(self, message: str):
        super().__init__(f"Database error: {message}")


class ValidationError(Advisor360Exception):
    """Raised when validation fails."""

    def __init__(self, message: str):
        super().__init__(f"Validation error: {message}")


class DuplicatePartnerError(Advisor360Exception):
    """Raised when trying to create a partner with duplicate name."""

    def __init__(self, message: str):
        super().__init__(f"Duplicate partner: {message}")


class PartnerHasCommissionsError(Advisor360Exception):
    """Raised when trying to delete a partner that has associated commissions."""

    def __init__(self, message: str):
        super().__init__(f"Partner has commissions: {message}")
