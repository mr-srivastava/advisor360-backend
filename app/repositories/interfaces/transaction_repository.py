"""Transaction repository interface defining transaction-specific data access operations."""

from abc import abstractmethod
from datetime import date
from typing import Optional

from ...domain.transaction import Transaction
from ...domain.value_objects.financial_year import FinancialYear
from ..base import BaseRepository


class ITransactionRepository(BaseRepository[Transaction]):
    """Interface for transaction repository defining transaction-specific operations.

    Extends the base repository interface with transaction-specific query methods
    for business logic requirements like financial year filtering, partner-based
    queries, and transaction analytics operations.
    """

    @abstractmethod
    async def get_by_partner_id(self, partner_id: str) -> list[Transaction]:
        """Retrieve all transactions for a specific partner.

        Args:
            partner_id: The unique identifier of the partner

        Returns:
            List of transactions for the partner

        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        pass

    @abstractmethod
    async def get_by_financial_year(
        self, financial_year: FinancialYear
    ) -> list[Transaction]:
        """Retrieve all transactions for a specific financial year.

        Args:
            financial_year: The financial year to filter by

        Returns:
            List of transactions in the financial year

        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        pass

    @abstractmethod
    async def get_by_partner_and_financial_year(
        self, partner_id: str, financial_year: FinancialYear
    ) -> list[Transaction]:
        """Retrieve transactions for a specific partner in a specific financial year.

        Args:
            partner_id: The unique identifier of the partner
            financial_year: The financial year to filter by

        Returns:
            List of transactions matching the criteria

        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        pass

    @abstractmethod
    async def get_by_date_range(
        self, start_date: date, end_date: date
    ) -> list[Transaction]:
        """Retrieve transactions within a specific date range.

        Args:
            start_date: The start date (inclusive)
            end_date: The end date (inclusive)

        Returns:
            List of transactions within the date range

        Raises:
            RepositoryError: If there's an error accessing the data store
            ValueError: If start_date is after end_date
        """
        pass

    @abstractmethod
    async def get_by_month_year(self, month: int, year: int) -> list[Transaction]:
        """Retrieve transactions for a specific month and year.

        Args:
            month: The month (1-12)
            year: The year

        Returns:
            List of transactions for the specified month and year

        Raises:
            RepositoryError: If there's an error accessing the data store
            ValueError: If month is not between 1-12
        """
        pass

    @abstractmethod
    async def get_total_amount_by_partner(
        self, partner_id: str, financial_year: Optional[FinancialYear] = None
    ) -> float:
        """Calculate total transaction amount for a partner, optionally filtered by financial year.

        Args:
            partner_id: The unique identifier of the partner
            financial_year: Optional financial year filter

        Returns:
            Total transaction amount for the partner

        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        pass

    @abstractmethod
    async def get_total_amount_by_financial_year(
        self, financial_year: FinancialYear
    ) -> float:
        """Calculate total transaction amount for a financial year.

        Args:
            financial_year: The financial year to calculate totals for

        Returns:
            Total transaction amount for the financial year

        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        pass

    @abstractmethod
    async def get_monthly_totals(
        self, financial_year: FinancialYear
    ) -> dict[str, float]:
        """Get monthly transaction totals for a financial year.

        Args:
            financial_year: The financial year to get monthly totals for

        Returns:
            Dictionary mapping month names to total amounts

        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        pass

    @abstractmethod
    async def get_partner_totals(
        self, financial_year: Optional[FinancialYear] = None
    ) -> dict[str, float]:
        """Get transaction totals by partner, optionally filtered by financial year.

        Args:
            financial_year: Optional financial year filter

        Returns:
            Dictionary mapping partner IDs to total amounts

        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        pass

    @abstractmethod
    async def get_recent_transactions(self, limit: int = 10) -> list[Transaction]:
        """Retrieve the most recent transactions.

        Args:
            limit: Maximum number of transactions to return

        Returns:
            List of recent transactions ordered by creation date (newest first)

        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        pass

    @abstractmethod
    async def search_by_description(self, search_term: str) -> list[Transaction]:
        """Search transactions by description text.

        Args:
            search_term: The text to search for in descriptions

        Returns:
            List of transactions with descriptions containing the search term

        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        pass

    @abstractmethod
    async def get_transaction_count_by_partner(
        self, partner_id: str, financial_year: Optional[FinancialYear] = None
    ) -> int:
        """Get count of transactions for a partner, optionally filtered by financial year.

        Args:
            partner_id: The unique identifier of the partner
            financial_year: Optional financial year filter

        Returns:
            Number of transactions for the partner

        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        pass

    @abstractmethod
    async def get_average_transaction_amount(
        self,
        partner_id: Optional[str] = None,
        financial_year: Optional[FinancialYear] = None,
    ) -> float:
        """Calculate average transaction amount, optionally filtered by partner and/or financial year.

        Args:
            partner_id: Optional partner ID filter
            financial_year: Optional financial year filter

        Returns:
            Average transaction amount

        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        pass
