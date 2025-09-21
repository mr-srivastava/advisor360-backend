"""Supabase implementation of the Commission repository."""

import logging
from datetime import date
from typing import Any, Optional

from postgrest.exceptions import APIError
from supabase import Client

from ...core.exceptions.repository_exceptions import RepositoryError
from ...domain.commission import Commission
from ...domain.value_objects.financial_year import FinancialYear
from ..interfaces.commission_repository import ICommissionRepository
from ..models.commission_model import CommissionModel
from .base_repository import BaseSupabaseRepository

logger = logging.getLogger(__name__)


class CommissionRepository(
    BaseSupabaseRepository[Commission, CommissionModel], ICommissionRepository
):
    """Supabase implementation of the Commission repository.

    Provides commission-specific data access operations using Supabase as the backend.
    Maps between Commission domain models and the entity_transactions table.
    """

    def __init__(self, supabase_client: Client):
        """Initialize the Commission repository.

        Args:
            supabase_client: Supabase client instance
        """
        super().__init__(supabase_client, "entity_transactions", CommissionModel)
        self._logger = logging.getLogger(f"{__name__}.CommissionRepository")

    async def get_by_partner_id(self, partner_id: str) -> list[Commission]:
        """Retrieve all commissions for a specific partner.

        Args:
            partner_id: The unique identifier of the partner

        Returns:
            List of commissions for the partner

        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        try:
            if not partner_id or not partner_id.strip():
                raise ValueError("Partner ID cannot be empty")

            self._logger.debug(f"Fetching commissions for partner: {partner_id}")

            response = (
                self._client.table(self._table_name)
                .select("*")
                .eq("entity_id", partner_id)
                .order("month", desc=True)
                .execute()
            )

            commissions = []
            for row in response.data:
                db_model = CommissionModel.from_database_row(row)
                commission = db_model.to_domain()
                commissions.append(commission)

            self._logger.debug(
                f"Retrieved {len(commissions)} commissions for partner {partner_id}"
            )
            return commissions

        except APIError as e:
            self._logger.error(
                f"Supabase API error retrieving commissions for partner {partner_id}: {e}"
            )
            raise RepositoryError(
                f"Failed to retrieve commissions for partner: {str(e)}"
            ) from e
        except Exception as e:
            self._logger.error(
                f"Unexpected error retrieving commissions for partner {partner_id}: {e}"
            )
            raise RepositoryError(
                f"Unexpected error retrieving commissions for partner: {str(e)}"
            ) from e

    async def get_by_financial_year(
        self, financial_year: FinancialYear
    ) -> list[Commission]:
        """Retrieve all commissions for a specific financial year.

        Args:
            financial_year: The financial year to filter by

        Returns:
            List of commissions in the financial year

        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        try:
            start_date = financial_year.get_start_date()
            end_date = financial_year.get_end_date()

            self._logger.debug(
                f"Fetching commissions for financial year: {financial_year}"
            )

            response = (
                self._client.table(self._table_name)
                .select("*")
                .gte("month", start_date.isoformat())
                .lte("month", end_date.isoformat())
                .order("month", desc=True)
                .execute()
            )

            commissions = []
            for row in response.data:
                db_model = CommissionModel.from_database_row(row)
                commission = db_model.to_domain()
                commissions.append(commission)

            self._logger.debug(
                f"Retrieved {len(commissions)} commissions for financial year {financial_year}"
            )
            return commissions

        except APIError as e:
            self._logger.error(
                f"Supabase API error retrieving commissions for FY {financial_year}: {e}"
            )
            raise RepositoryError(
                f"Failed to retrieve commissions for financial year: {str(e)}"
            ) from e
        except Exception as e:
            self._logger.error(
                f"Unexpected error retrieving commissions for FY {financial_year}: {e}"
            )
            raise RepositoryError(
                f"Unexpected error retrieving commissions for financial year: {str(e)}"
            ) from e

    async def get_by_partner_and_financial_year(
        self, partner_id: str, financial_year: FinancialYear
    ) -> list[Commission]:
        """Retrieve commissions for a specific partner in a specific financial year.

        Args:
            partner_id: The unique identifier of the partner
            financial_year: The financial year to filter by

        Returns:
            List of commissions matching the criteria

        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        try:
            if not partner_id or not partner_id.strip():
                raise ValueError("Partner ID cannot be empty")

            start_date = financial_year.get_start_date()
            end_date = financial_year.get_end_date()

            self._logger.debug(
                f"Fetching commissions for partner {partner_id} in FY {financial_year}"
            )

            response = (
                self._client.table(self._table_name)
                .select("*")
                .eq("entity_id", partner_id)
                .gte("month", start_date.isoformat())
                .lte("month", end_date.isoformat())
                .order("month", desc=True)
                .execute()
            )

            commissions = []
            for row in response.data:
                db_model = CommissionModel.from_database_row(row)
                commission = db_model.to_domain()
                commissions.append(commission)

            self._logger.debug(
                f"Retrieved {len(commissions)} commissions for partner {partner_id} in FY {financial_year}"
            )
            return commissions

        except APIError as e:
            self._logger.error(
                f"Supabase API error retrieving commissions for partner {partner_id} in FY {financial_year}: {e}"
            )
            raise RepositoryError(
                f"Failed to retrieve commissions for partner and financial year: {str(e)}"
            ) from e
        except Exception as e:
            self._logger.error(
                f"Unexpected error retrieving commissions for partner {partner_id} in FY {financial_year}: {e}"
            )
            raise RepositoryError(
                f"Unexpected error retrieving commissions for partner and financial year: {str(e)}"
            ) from e

    async def get_by_date_range(
        self, start_date: date, end_date: date
    ) -> list[Commission]:
        """Retrieve commissions within a specific date range.

        Args:
            start_date: The start date (inclusive)
            end_date: The end date (inclusive)

        Returns:
            List of commissions within the date range

        Raises:
            RepositoryError: If there's an error accessing the data store
            ValueError: If start_date is after end_date
        """
        try:
            if start_date > end_date:
                raise ValueError("Start date cannot be after end date")

            self._logger.debug(f"Fetching commissions from {start_date} to {end_date}")

            response = (
                self._client.table(self._table_name)
                .select("*")
                .gte("month", start_date.isoformat())
                .lte("month", end_date.isoformat())
                .order("month", desc=True)
                .execute()
            )

            commissions = []
            for row in response.data:
                db_model = CommissionModel.from_database_row(row)
                commission = db_model.to_domain()
                commissions.append(commission)

            self._logger.debug(
                f"Retrieved {len(commissions)} commissions in date range"
            )
            return commissions

        except APIError as e:
            self._logger.error(
                f"Supabase API error retrieving commissions for date range: {e}"
            )
            raise RepositoryError(
                f"Failed to retrieve commissions for date range: {str(e)}"
            ) from e
        except ValueError:
            raise
        except Exception as e:
            self._logger.error(
                f"Unexpected error retrieving commissions for date range: {e}"
            )
            raise RepositoryError(
                f"Unexpected error retrieving commissions for date range: {str(e)}"
            ) from e

    async def get_by_month_year(self, month: int, year: int) -> list[Commission]:
        """Retrieve commissions for a specific month and year.

        Args:
            month: The month (1-12)
            year: The year

        Returns:
            List of commissions for the specified month and year

        Raises:
            RepositoryError: If there's an error accessing the data store
            ValueError: If month is not between 1-12
        """
        try:
            if month < 1 or month > 12:
                raise ValueError("Month must be between 1 and 12")

            # Create date range for the month
            start_date = date(year, month, 1)
            if month == 12:
                end_date = date(year + 1, 1, 1)
            else:
                end_date = date(year, month + 1, 1)

            self._logger.debug(f"Fetching commissions for {month}/{year}")

            response = (
                self._client.table(self._table_name)
                .select("*")
                .gte("month", start_date.isoformat())
                .lt("month", end_date.isoformat())
                .order("month", desc=True)
                .execute()
            )

            commissions = []
            for row in response.data:
                db_model = CommissionModel.from_database_row(row)
                commission = db_model.to_domain()
                commissions.append(commission)

            self._logger.debug(
                f"Retrieved {len(commissions)} commissions for {month}/{year}"
            )
            return commissions

        except APIError as e:
            self._logger.error(
                f"Supabase API error retrieving commissions for {month}/{year}: {e}"
            )
            raise RepositoryError(
                f"Failed to retrieve commissions for month/year: {str(e)}"
            ) from e
        except ValueError:
            raise
        except Exception as e:
            self._logger.error(
                f"Unexpected error retrieving commissions for {month}/{year}: {e}"
            )
            raise RepositoryError(
                f"Unexpected error retrieving commissions for month/year: {str(e)}"
            ) from e

    async def get_total_amount_by_partner(
        self, partner_id: str, financial_year: Optional[FinancialYear] = None
    ) -> float:
        """Calculate total commission amount for a partner, optionally filtered by financial year.

        Args:
            partner_id: The unique identifier of the partner
            financial_year: Optional financial year filter

        Returns:
            Total commission amount for the partner

        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        try:
            if not partner_id or not partner_id.strip():
                raise ValueError("Partner ID cannot be empty")

            self._logger.debug(f"Calculating total amount for partner {partner_id}")

            query = (
                self._client.table(self._table_name)
                .select("amount")
                .eq("entity_id", partner_id)
            )

            if financial_year:
                start_date = financial_year.get_start_date()
                end_date = financial_year.get_end_date()
                query = query.gte("month", start_date.isoformat()).lte(
                    "month", end_date.isoformat()
                )

            response = query.execute()

            total = sum(row["amount"] for row in response.data)

            self._logger.debug(f"Total amount for partner {partner_id}: {total}")
            return total

        except APIError as e:
            self._logger.error(
                f"Supabase API error calculating total for partner {partner_id}: {e}"
            )
            raise RepositoryError(
                f"Failed to calculate total for partner: {str(e)}"
            ) from e
        except Exception as e:
            self._logger.error(
                f"Unexpected error calculating total for partner {partner_id}: {e}"
            )
            raise RepositoryError(
                f"Unexpected error calculating total for partner: {str(e)}"
            ) from e

    async def get_total_amount_by_financial_year(
        self, financial_year: FinancialYear
    ) -> float:
        """Calculate total commission amount for a financial year.

        Args:
            financial_year: The financial year to calculate totals for

        Returns:
            Total commission amount for the financial year

        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        try:
            start_date = financial_year.get_start_date()
            end_date = financial_year.get_end_date()

            self._logger.debug(
                f"Calculating total amount for financial year {financial_year}"
            )

            response = (
                self._client.table(self._table_name)
                .select("amount")
                .gte("month", start_date.isoformat())
                .lte("month", end_date.isoformat())
                .execute()
            )

            total = sum(row["amount"] for row in response.data)

            self._logger.debug(
                f"Total amount for financial year {financial_year}: {total}"
            )
            return total

        except APIError as e:
            self._logger.error(
                f"Supabase API error calculating total for FY {financial_year}: {e}"
            )
            raise RepositoryError(
                f"Failed to calculate total for financial year: {str(e)}"
            ) from e
        except Exception as e:
            self._logger.error(
                f"Unexpected error calculating total for FY {financial_year}: {e}"
            )
            raise RepositoryError(
                f"Unexpected error calculating total for financial year: {str(e)}"
            ) from e

    async def get_monthly_totals(
        self, financial_year: FinancialYear
    ) -> dict[str, float]:
        """Get monthly commission totals for a financial year.

        Args:
            financial_year: The financial year to get monthly totals for

        Returns:
            Dictionary mapping month names to total amounts

        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        try:
            start_date = financial_year.get_start_date()
            end_date = financial_year.get_end_date()

            self._logger.debug(
                f"Calculating monthly totals for financial year {financial_year}"
            )

            response = (
                self._client.table(self._table_name)
                .select("month, amount")
                .gte("month", start_date.isoformat())
                .lte("month", end_date.isoformat())
                .execute()
            )

            monthly_totals = {}
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

            for row in response.data:
                db_model = CommissionModel.from_database_row(row)
                month_name = months[db_model.month.month - 1]

                if month_name not in monthly_totals:
                    monthly_totals[month_name] = 0.0
                monthly_totals[month_name] += row["amount"]

            self._logger.debug(
                f"Monthly totals for FY {financial_year}: {monthly_totals}"
            )
            return monthly_totals

        except APIError as e:
            self._logger.error(
                f"Supabase API error calculating monthly totals for FY {financial_year}: {e}"
            )
            raise RepositoryError(
                f"Failed to calculate monthly totals: {str(e)}"
            ) from e
        except Exception as e:
            self._logger.error(
                f"Unexpected error calculating monthly totals for FY {financial_year}: {e}"
            )
            raise RepositoryError(
                f"Unexpected error calculating monthly totals: {str(e)}"
            ) from e

    async def get_partner_totals(
        self, financial_year: Optional[FinancialYear] = None
    ) -> dict[str, float]:
        """Get commission totals by partner, optionally filtered by financial year.

        Args:
            financial_year: Optional financial year filter

        Returns:
            Dictionary mapping partner IDs to total amounts

        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        try:
            self._logger.debug(f"Calculating partner totals for FY {financial_year}")

            query = self._client.table(self._table_name).select("entity_id, amount")

            if financial_year:
                start_date = financial_year.get_start_date()
                end_date = financial_year.get_end_date()
                query = query.gte("month", start_date.isoformat()).lte(
                    "month", end_date.isoformat()
                )

            response = query.execute()

            partner_totals = {}
            for row in response.data:
                partner_id = row["entity_id"]
                amount = row["amount"]

                if partner_id not in partner_totals:
                    partner_totals[partner_id] = 0.0
                partner_totals[partner_id] += amount

            self._logger.debug(f"Partner totals: {partner_totals}")
            return partner_totals

        except APIError as e:
            self._logger.error(f"Supabase API error calculating partner totals: {e}")
            raise RepositoryError(
                f"Failed to calculate partner totals: {str(e)}"
            ) from e
        except Exception as e:
            self._logger.error(f"Unexpected error calculating partner totals: {e}")
            raise RepositoryError(
                f"Unexpected error calculating partner totals: {str(e)}"
            ) from e

    async def get_recent_commissions(self, limit: int = 10) -> list[Commission]:
        """Retrieve the most recent commissions.

        Args:
            limit: Maximum number of commissions to return

        Returns:
            List of recent commissions ordered by creation date (newest first)

        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        try:
            if limit <= 0:
                raise ValueError("Limit must be positive")

            self._logger.debug(f"Fetching {limit} recent commissions")

            response = (
                self._client.table(self._table_name)
                .select("*")
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            commissions = []
            for row in response.data:
                db_model = CommissionModel.from_database_row(row)
                commission = db_model.to_domain()
                commissions.append(commission)

            self._logger.debug(f"Retrieved {len(commissions)} recent commissions")
            return commissions

        except APIError as e:
            self._logger.error(f"Supabase API error retrieving recent commissions: {e}")
            raise RepositoryError(
                f"Failed to retrieve recent commissions: {str(e)}"
            ) from e
        except ValueError:
            raise
        except Exception as e:
            self._logger.error(f"Unexpected error retrieving recent commissions: {e}")
            raise RepositoryError(
                f"Unexpected error retrieving recent commissions: {str(e)}"
            ) from e

    async def search_by_description(self, search_term: str) -> list[Commission]:
        """Search commissions by description text.

        Args:
            search_term: The text to search for in descriptions

        Returns:
            List of commissions with descriptions containing the search term

        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        try:
            if not search_term or not search_term.strip():
                raise ValueError("Search term cannot be empty")

            search_term = search_term.strip()
            self._logger.debug(f"Searching commissions by description: {search_term}")

            response = (
                self._client.table(self._table_name)
                .select("*")
                .ilike("description", f"%{search_term}%")
                .order("created_at", desc=True)
                .execute()
            )

            commissions = []
            for row in response.data:
                db_model = CommissionModel.from_database_row(row)
                commission = db_model.to_domain()
                commissions.append(commission)

            self._logger.debug(
                f"Found {len(commissions)} commissions matching description search"
            )
            return commissions

        except APIError as e:
            self._logger.error(
                f"Supabase API error searching commissions by description: {e}"
            )
            raise RepositoryError(
                f"Failed to search commissions by description: {str(e)}"
            ) from e
        except ValueError:
            raise
        except Exception as e:
            self._logger.error(
                f"Unexpected error searching commissions by description: {e}"
            )
            raise RepositoryError(
                f"Unexpected error searching commissions by description: {str(e)}"
            ) from e

    async def exists_by_partner_and_month(self, partner_id: str, transaction_date: date) -> Optional[Commission]:
        """Check if a commission already exists for a partner in the same month/year.

        Args:
            partner_id: The unique identifier of the partner
            transaction_date: The transaction date to check

        Returns:
            Existing commission if found, None otherwise

        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        try:
            if not partner_id or not partner_id.strip():
                raise ValueError("Partner ID cannot be empty")

            # Create date range for the month
            start_date = transaction_date.replace(day=1)
            if transaction_date.month == 12:
                end_date = date(transaction_date.year + 1, 1, 1)
            else:
                end_date = date(transaction_date.year, transaction_date.month + 1, 1)

            self._logger.debug(
                f"Checking for existing commission for partner {partner_id} in {transaction_date.strftime('%B %Y')}"
            )

            response = (
                self._client.table(self._table_name)
                .select("*")
                .eq("entity_id", partner_id)
                .gte("month", start_date.isoformat())
                .lt("month", end_date.isoformat())
                .limit(1)
                .execute()
            )

            if response.data:
                db_model = CommissionModel.from_database_row(response.data[0])
                commission = db_model.to_domain()
                self._logger.debug(
                    f"Found existing commission {commission.id} for partner {partner_id} in {transaction_date.strftime('%B %Y')}"
                )
                return commission

            self._logger.debug(
                f"No existing commission found for partner {partner_id} in {transaction_date.strftime('%B %Y')}"
            )
            return None

        except APIError as e:
            self._logger.error(
                f"Supabase API error checking commission existence: {e}"
            )
            raise RepositoryError(
                f"Failed to check commission existence: {str(e)}"
            ) from e
        except ValueError:
            raise
        except Exception as e:
            self._logger.error(
                f"Unexpected error checking commission existence: {e}"
            )
            raise RepositoryError(
                f"Unexpected error checking commission existence: {str(e)}"
            ) from e

    async def get_all_ordered(
        self,
        order_by: str = "created_at",
        ascending: bool = False,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[Commission]:
        """Retrieve all commissions with ordering, handling pagination.

        Args:
            order_by: Column to order by (default: created_at)
            ascending: Whether to sort in ascending order (default: False for descending)
            filters: Optional dictionary of filters to apply

        Returns:
            List of all commissions ordered as specified

        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        try:
            self._logger.debug(
                f"Fetching all commissions ordered by {order_by} (asc={ascending}) with filters: {filters}"
            )

            # Use the base class method that handles pagination
            commissions = await super().get_all_ordered(order_by, ascending, filters)

            self._logger.debug(f"Retrieved {len(commissions)} ordered commissions")
            return commissions

        except Exception as e:
            self._logger.error(f"Unexpected error retrieving ordered commissions: {e}")
            raise RepositoryError(
                f"Unexpected error retrieving ordered commissions: {str(e)}"
            ) from e
