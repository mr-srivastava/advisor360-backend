"""API Data Transfer Objects (DTOs) for request and response models.

This module contains all the DTOs used for API communication,
separated from domain models to maintain clean architecture.
"""

from .commission_dtos import (
    CommissionDetailResponse,
    CommissionListResponse,
    CommissionResponse,
    CreateCommissionRequest,
    UpdateCommissionRequest,
)
from .common_dtos import BaseResponse, ErrorResponse, PaginatedResponse, SuccessResponse
from .dashboard_dtos import (
    DashboardAnalyticsResponse,
    DashboardMapper,
    DashboardOverviewResponse,
    DashboardQueryParams,
    FinancialYearPathParam,
    FinancialYearsResponse,
    FYMetricsResponse,
    PerformanceMetricsResponse,
    RecentActivityResponse,
)
from .mappers import (
    AnalyticsMapper,
    DomainToDTOMapper,
    ValidationMapper,
    map_commission_with_partner,
    map_commissions_with_partners,
    map_transaction_with_partner,
    map_transactions_with_partners,
)
from .partner_dtos import (
    CreatePartnerRequest,
    PartnerDetailResponse,
    PartnerListResponse,
    PartnerResponse,
    UpdatePartnerRequest,
)
from .transaction_dtos import (
    CreateTransactionRequest,
    TransactionDetailResponse,
    TransactionListResponse,
    TransactionResponse,
    UpdateTransactionRequest,
)

__all__ = [
    # Commission DTOs
    "CreateCommissionRequest",
    "UpdateCommissionRequest",
    "CommissionResponse",
    "CommissionListResponse",
    "CommissionDetailResponse",
    # Partner DTOs
    "CreatePartnerRequest",
    "UpdatePartnerRequest",
    "PartnerResponse",
    "PartnerListResponse",
    "PartnerDetailResponse",
    # Transaction DTOs
    "CreateTransactionRequest",
    "UpdateTransactionRequest",
    "TransactionResponse",
    "TransactionListResponse",
    "TransactionDetailResponse",
    # Dashboard DTOs
    "DashboardQueryParams",
    "FinancialYearPathParam",
    "DashboardOverviewResponse",
    "FYMetricsResponse",
    "PerformanceMetricsResponse",
    "RecentActivityResponse",
    "FinancialYearsResponse",
    "DashboardAnalyticsResponse",
    "DashboardMapper",
    # Common DTOs
    "BaseResponse",
    "ErrorResponse",
    "PaginatedResponse",
    "SuccessResponse",
    # Mappers
    "DomainToDTOMapper",
    "AnalyticsMapper",
    "ValidationMapper",
    "map_commission_with_partner",
    "map_commissions_with_partners",
    "map_transaction_with_partner",
    "map_transactions_with_partners",
]
