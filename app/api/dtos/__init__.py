"""
API Data Transfer Objects (DTOs) for request and response models.

This module contains all the DTOs used for API communication,
separated from domain models to maintain clean architecture.
"""

from .commission_dtos import (
    CreateCommissionRequest,
    UpdateCommissionRequest,
    CommissionResponse,
    CommissionListResponse,
    CommissionDetailResponse
)

from .partner_dtos import (
    CreatePartnerRequest,
    UpdatePartnerRequest,
    PartnerResponse,
    PartnerListResponse,
    PartnerDetailResponse
)

from .transaction_dtos import (
    CreateTransactionRequest,
    UpdateTransactionRequest,
    TransactionResponse,
    TransactionListResponse,
    TransactionDetailResponse
)

from .dashboard_dtos import (
    DashboardQueryParams,
    FinancialYearPathParam,
    DashboardOverviewResponse,
    FYMetricsResponse,
    PerformanceMetricsResponse,
    RecentActivityResponse,
    FinancialYearsResponse,
    DashboardAnalyticsResponse,
    DashboardMapper
)

from .common_dtos import (
    BaseResponse,
    ErrorResponse,
    PaginatedResponse,
    SuccessResponse
)

from .mappers import (
    DomainToDTOMapper,
    AnalyticsMapper,
    ValidationMapper,
    map_commission_with_partner,
    map_commissions_with_partners,
    map_transaction_with_partner,
    map_transactions_with_partners
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
    "map_transactions_with_partners"
]