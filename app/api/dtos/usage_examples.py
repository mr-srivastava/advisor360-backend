"""Usage examples for API DTOs.

This file demonstrates how to use the DTOs in API routes and services.
It serves as documentation and reference for developers.
"""

# Example imports (these would be in your actual route files)
from app.domain.commission import Commission
from app.domain.partner import EntityType, Partner

from .commission_dtos import (
    CommissionListResponse,
    CommissionResponse,
    CreateCommissionRequest,
)
from .common_dtos import DataResponse, ListResponse
from .mappers import DomainToDTOMapper
from .partner_dtos import CreatePartnerRequest, PartnerResponse


# Example 1: Creating a commission from API request
def example_create_commission():
    """Example of creating a commission from API request."""
    # This would come from FastAPI request body
    request_data = {
        "partner_id": "partner-123",
        "amount": 1500.0,
        "currency": "INR",
        "transaction_date": "2024-06-15",
        "description": "Monthly commission",
    }

    # Parse and validate request
    create_request = CreateCommissionRequest(**request_data)

    # Convert to domain model
    commission = create_request.to_domain()

    # After saving to repository, convert back to response
    # (Assuming you have a partner from repository)
    partner = Partner(
        id="partner-123", name="ABC Mutual Funds", entity_type=EntityType.MUTUAL_FUNDS
    )

    response = CommissionResponse.from_domain(commission, partner)

    return DataResponse[CommissionResponse](
        data=response, message="Commission created successfully"
    )


# Example 2: Listing commissions with partners
def example_list_commissions():
    """Example of listing commissions with partner data."""
    # These would come from your service/repository
    commissions: list[Commission] = []  # From repository
    partners: list[Partner] = []  # From repository

    # Convert to response DTOs
    commission_responses = DomainToDTOMapper.commissions_to_response_list(
        commissions, partners
    )

    # Create summary
    summary = DomainToDTOMapper.create_commission_summary(commissions)

    return CommissionListResponse(
        data=commission_responses,
        count=len(commission_responses),
        summary=summary,
        message=f"Retrieved {len(commission_responses)} commissions",
    )


# Example 3: Partner creation and response
def example_create_partner():
    """Example of creating a partner from API request."""
    request_data = {"name": "XYZ Insurance", "entity_type": "Life Insurance"}

    create_request = CreatePartnerRequest(**request_data)

    # Generate ID (this would typically be done by your service)
    import uuid

    partner_id = str(uuid.uuid4())

    # Convert to domain model
    partner = create_request.to_domain(partner_id)

    # Convert to response
    response = PartnerResponse.from_domain(partner)

    return DataResponse[PartnerResponse](
        data=response, message="Partner created successfully"
    )


# Example 4: Error handling with DTOs
def example_error_handling():
    """Example of error handling with DTOs."""
    from .common_dtos import ErrorDetail, ErrorResponse

    try:
        # Some operation that might fail
        request_data = {
            "partner_id": "",  # Invalid empty partner_id
            "amount": -100.0,  # Invalid negative amount
            "transaction_date": "2025-12-31",  # Future date
        }

        create_request = CreateCommissionRequest(**request_data)

    except ValueError:
        # Convert validation errors to standardized format
        return ErrorResponse(
            message="Validation failed",
            details=[
                ErrorDetail(
                    field="partner_id",
                    message="Partner ID cannot be empty",
                    code="REQUIRED_FIELD",
                ),
                ErrorDetail(
                    field="amount",
                    message="Amount must be positive",
                    code="INVALID_VALUE",
                ),
                ErrorDetail(
                    field="transaction_date",
                    message="Transaction date cannot be in the future",
                    code="INVALID_DATE",
                ),
            ],
        )


# Example 5: Using mappers for complex operations
def example_complex_mapping():
    """Example of complex mapping operations."""
    from .mappers import AnalyticsMapper

    # Sample data (would come from repository)
    commissions: list[Commission] = []
    partners: list[Partner] = []

    # Create monthly analytics
    monthly_data = AnalyticsMapper.create_monthly_commission_data(
        commissions, include_growth=True
    )

    # Create partner performance data
    partner_data = AnalyticsMapper.create_partner_commission_data(commissions, partners)

    # Create partner performance analytics
    performance_data = AnalyticsMapper.create_partner_performance_data(
        partners, commissions
    )

    return {
        "monthly_analytics": monthly_data,
        "partner_analytics": partner_data,
        "performance_analytics": performance_data,
    }


# Example 6: Dashboard data mapping
def example_dashboard_mapping():
    """Example of dashboard data mapping."""
    from .dashboard_dtos import DashboardMapper

    # Create stat cards for dashboard
    total_commissions = 150000.0
    growth_percentage = 15.2

    stat_card = DashboardMapper.create_stat_card(
        id="total_commissions",
        title="Total Commissions",
        value=DashboardMapper.format_currency(total_commissions),
        subtitle="This month",
        icon="currency",
        trend=DashboardMapper.create_trend_data(growth_percentage),
    )

    return stat_card


# Example 7: Pagination with DTOs
def example_pagination():
    """Example of pagination with DTOs."""
    from .common_dtos import PaginatedResponse, PaginationMeta

    # Sample data
    commissions: list[Commission] = []
    partners: list[Partner] = []

    # Pagination parameters (would come from query params)
    page = 1
    per_page = 10
    total_items = 100

    # Convert to response DTOs
    commission_responses = DomainToDTOMapper.commissions_to_response_list(
        commissions, partners
    )

    # Create pagination metadata
    total_pages = (total_items + per_page - 1) // per_page
    pagination_meta = PaginationMeta(
        page=page,
        per_page=per_page,
        total=total_items,
        pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )

    return PaginatedResponse[CommissionResponse](
        data=commission_responses,
        meta=pagination_meta,
        message=f"Retrieved page {page} of {total_pages}",
    )


# Example 8: Validation with custom validators
def example_custom_validation():
    """Example of custom validation in DTOs."""
    from datetime import date

    from pydantic import BaseModel, Field, validator

    class CustomCommissionRequest(BaseModel):
        partner_id: str = Field(..., min_length=1)
        amount: float = Field(..., gt=0)
        transaction_date: date

        @validator("transaction_date")
        def validate_transaction_date(cls, v):
            if v > date.today():
                raise ValueError("Transaction date cannot be in the future")

            # Custom business rule: no transactions on weekends
            if v.weekday() >= 5:  # Saturday = 5, Sunday = 6
                raise ValueError("Transactions cannot be created on weekends")

            return v

        @validator("amount")
        def validate_amount(cls, v):
            # Custom business rule: minimum commission amount
            if v < 100:
                raise ValueError("Minimum commission amount is ₹100")

            # Maximum commission amount
            if v > 1000000:
                raise ValueError("Maximum commission amount is ₹10,00,000")

            return v

    # Usage
    try:
        request = CustomCommissionRequest(
            partner_id="partner-123",
            amount=50.0,  # Below minimum
            transaction_date=date(2024, 6, 15),  # Assuming it's a weekend
        )
    except ValueError as e:
        print(f"Validation error: {e}")


# Example 9: Response formatting utilities
def example_response_formatting():
    """Example of response formatting utilities."""
    from .common_dtos import SuccessResponse

    def format_success_response(message: str) -> SuccessResponse:
        """Format a simple success response."""
        return SuccessResponse(message=message)

    def format_data_response(data, message: str):
        """Format a data response."""
        return DataResponse(data=data, message=message)

    def format_list_response(items: list, message: str):
        """Format a list response."""
        return ListResponse(data=items, count=len(items), message=message)

    # Usage examples
    success = format_success_response("Operation completed successfully")
    data_resp = format_data_response({"id": "123"}, "Data retrieved")
    list_resp = format_list_response([1, 2, 3], "Items retrieved")

    return {"success": success, "data": data_resp, "list": list_resp}


if __name__ == "__main__":
    # Run examples for testing
    print("Running DTO usage examples...")

    # These would normally be called from your API routes
    # example_create_commission()
    # example_list_commissions()
    # example_create_partner()

    print("Examples completed successfully!")
