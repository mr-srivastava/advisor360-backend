"""Centralized mapping utilities for converting between domain models and DTOs.

This module provides a unified interface for all mapping operations,
ensuring consistency and reducing code duplication across the application.
"""

from datetime import datetime
from typing import Any, Optional

from app.domain.commission import Commission
from app.domain.partner import Partner
from app.domain.transaction import Transaction

from .commission_dtos import (
    CommissionMapper,
    CommissionResponse,
    CommissionSummary,
    MonthlyCommissionData,
    PartnerCommissionData,
)
from .partner_dtos import (
    EntityTypeResponse,
    PartnerMapper,
    PartnerPerformanceData,
    PartnerResponse,
    PartnerSummary,
)
from .transaction_dtos import (
    TransactionMapper,
    TransactionResponse,
    TransactionSummary,
)


class DomainToDTOMapper:
    """Centralized mapper for converting domain models to DTOs.

    This class provides a single point of access for all mapping operations,
    making it easier to maintain consistency and handle complex mappings.
    """

    # Commission mappings
    @staticmethod
    def commission_to_response(
        commission: Commission, partner: Optional[Partner] = None
    ) -> CommissionResponse:
        """Convert Commission domain model to CommissionResponse DTO."""
        return CommissionMapper.to_response(commission, partner)

    @staticmethod
    def commissions_to_response_list(
        commissions: list[Commission], partners: Optional[list[Partner]] = None
    ) -> list[CommissionResponse]:
        """Convert list of Commission domain models to CommissionResponse DTOs."""
        return CommissionMapper.to_response_list(commissions, partners)

    @staticmethod
    def create_commission_summary(
        commissions: list[Commission], financial_year: Optional[str] = None
    ) -> CommissionSummary:
        """Create CommissionSummary from list of Commission domain models."""
        return CommissionMapper.create_summary(commissions, financial_year)

    # Partner mappings
    @staticmethod
    def partner_to_response(partner: Partner) -> PartnerResponse:
        """Convert Partner domain model to PartnerResponse DTO."""
        return PartnerMapper.to_response(partner)

    @staticmethod
    def partners_to_response_list(partners: list[Partner]) -> list[PartnerResponse]:
        """Convert list of Partner domain models to PartnerResponse DTOs."""
        return PartnerMapper.to_response_list(partners)

    @staticmethod
    def create_partner_summary(partners: list[Partner]) -> PartnerSummary:
        """Create PartnerSummary from list of Partner domain models."""
        return PartnerMapper.create_summary(partners)

    @staticmethod
    def get_entity_types() -> list[EntityTypeResponse]:
        """Get all available entity types as DTOs."""
        return PartnerMapper.get_entity_types()

    # Transaction mappings
    @staticmethod
    def transaction_to_response(
        transaction: Transaction, partner: Optional[Partner] = None
    ) -> TransactionResponse:
        """Convert Transaction domain model to TransactionResponse DTO."""
        return TransactionMapper.to_response(transaction, partner)

    @staticmethod
    def transactions_to_response_list(
        transactions: list[Transaction], partners: Optional[list[Partner]] = None
    ) -> list[TransactionResponse]:
        """Convert list of Transaction domain models to TransactionResponse DTOs."""
        return TransactionMapper.to_response_list(transactions, partners)

    @staticmethod
    def create_transaction_summary(
        transactions: list[Transaction], financial_year: Optional[str] = None
    ) -> TransactionSummary:
        """Create TransactionSummary from list of Transaction domain models."""
        return TransactionMapper.create_summary(transactions, financial_year)


class AnalyticsMapper:
    """Specialized mapper for analytics and aggregation DTOs.

    Handles complex mappings for dashboard and reporting functionality.
    """

    @staticmethod
    def create_monthly_commission_data(
        commissions: list[Commission], include_growth: bool = True
    ) -> list[MonthlyCommissionData]:
        """Create monthly commission aggregation data."""
        monthly_data = {}

        for commission in commissions:
            month_key = (
                f"{commission.get_year()}-{commission.transaction_date.month:02d}"
            )
            month_name = commission.get_month_name()
            year = commission.get_year()

            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    "month": month_name,
                    "year": year,
                    "total_amount": 0.0,
                    "count": 0,
                }

            monthly_data[month_key]["total_amount"] += commission.amount.to_float()
            monthly_data[month_key]["count"] += 1

        # Convert to list and sort by date
        result = []
        sorted_keys = sorted(monthly_data.keys())

        for i, key in enumerate(sorted_keys):
            data = monthly_data[key]
            growth_percentage = None

            if include_growth and i > 0:
                prev_key = sorted_keys[i - 1]
                prev_total = monthly_data[prev_key]["total_amount"]
                if prev_total > 0:
                    growth_percentage = (
                        (data["total_amount"] - prev_total) / prev_total
                    ) * 100

            result.append(
                MonthlyCommissionData(
                    month=data["month"],
                    year=data["year"],
                    total_amount=data["total_amount"],
                    count=data["count"],
                    growth_percentage=growth_percentage,
                )
            )

        return result

    @staticmethod
    def create_partner_commission_data(
        commissions: list[Commission], partners: list[Partner]
    ) -> list[PartnerCommissionData]:
        """Create partner-wise commission aggregation data."""
        partner_map = {p.id: p for p in partners}
        partner_data = {}
        total_amount = sum(c.amount.to_float() for c in commissions)

        for commission in commissions:
            partner_id = commission.partner_id
            partner = partner_map.get(partner_id)

            if partner_id not in partner_data:
                partner_data[partner_id] = {
                    "partner_name": partner.name if partner else "Unknown",
                    "entity_type": partner.entity_type.value if partner else "Unknown",
                    "total_amount": 0.0,
                    "count": 0,
                }

            partner_data[partner_id]["total_amount"] += commission.amount.to_float()
            partner_data[partner_id]["count"] += 1

        # Convert to list and calculate percentages
        result = []
        for partner_id, data in partner_data.items():
            percentage = (
                (data["total_amount"] / total_amount * 100) if total_amount > 0 else 0
            )

            result.append(
                PartnerCommissionData(
                    partner_id=partner_id,
                    partner_name=data["partner_name"],
                    entity_type=data["entity_type"],
                    total_amount=data["total_amount"],
                    count=data["count"],
                    percentage_of_total=percentage,
                )
            )

        # Sort by total amount descending
        result.sort(key=lambda x: x.total_amount, reverse=True)
        return result

    @staticmethod
    def create_partner_performance_data(
        partners: list[Partner], commissions: list[Commission]
    ) -> list[PartnerPerformanceData]:
        """Create partner performance analytics data."""
        partner_performance = {}

        # Initialize partner data
        for partner in partners:
            partner_performance[partner.id] = {
                "partner": partner,
                "total_commissions": 0.0,
                "commission_count": 0,
                "last_commission_date": None,
            }

        # Aggregate commission data
        for commission in commissions:
            if commission.partner_id in partner_performance:
                data = partner_performance[commission.partner_id]
                data["total_commissions"] += commission.amount.to_float()
                data["commission_count"] += 1

                if (
                    data["last_commission_date"] is None
                    or commission.created_at > data["last_commission_date"]
                ):
                    data["last_commission_date"] = commission.created_at

        # Convert to list and rank
        result = []
        sorted_partners = sorted(
            partner_performance.items(),
            key=lambda x: x[1]["total_commissions"],
            reverse=True,
        )

        for rank, (partner_id, data) in enumerate(sorted_partners, 1):
            partner = data["partner"]
            total_commissions = data["total_commissions"]
            commission_count = data["commission_count"]

            result.append(
                PartnerPerformanceData(
                    partner_id=partner_id,
                    partner_name=partner.name,
                    entity_type=partner.entity_type.value,
                    total_commissions=total_commissions,
                    commission_count=commission_count,
                    average_commission=(
                        total_commissions / commission_count
                        if commission_count > 0
                        else 0.0
                    ),
                    last_commission_date=data["last_commission_date"],
                    performance_rank=rank,
                )
            )

        return result


class ValidationMapper:
    """Mapper for validation and error handling DTOs.

    Provides utilities for converting validation errors and exceptions
    to standardized error response formats.
    """

    @staticmethod
    def validation_error_to_dto(
        field: str, message: str, value: Any = None
    ) -> dict[str, Any]:
        """Convert validation error to DTO format."""
        return {"field": field, "message": message, "value": value}

    @staticmethod
    def domain_exception_to_error_response(
        exception: Exception, request_id: Optional[str] = None
    ) -> dict[str, Any]:
        """Convert domain exception to error response format."""
        return {
            "success": False,
            "message": str(exception),
            "details": [
                {
                    "field": None,
                    "message": str(exception),
                    "code": exception.__class__.__name__,
                }
            ],
            "timestamp": datetime.now(),
            "request_id": request_id,
        }


# Convenience functions for common operations
def map_commission_with_partner(
    commission: Commission, partners: list[Partner]
) -> CommissionResponse:
    """Map a single commission with its partner data."""
    partner = next((p for p in partners if p.id == commission.partner_id), None)
    return DomainToDTOMapper.commission_to_response(commission, partner)


def map_commissions_with_partners(
    commissions: list[Commission], partners: list[Partner]
) -> list[CommissionResponse]:
    """Map multiple commissions with their partner data."""
    return DomainToDTOMapper.commissions_to_response_list(commissions, partners)


def map_transaction_with_partner(
    transaction: Transaction, partners: list[Partner]
) -> TransactionResponse:
    """Map a single transaction with its partner data."""
    partner = next((p for p in partners if p.id == transaction.partner_id), None)
    return DomainToDTOMapper.transaction_to_response(transaction, partner)


def map_transactions_with_partners(
    transactions: list[Transaction], partners: list[Partner]
) -> list[TransactionResponse]:
    """Map multiple transactions with their partner data."""
    return DomainToDTOMapper.transactions_to_response_list(transactions, partners)
