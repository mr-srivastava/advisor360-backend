"""
Service interfaces for the application.

This module contains all service interface definitions that define the contracts
for business logic operations in the application.
"""

from .commission_service import ICommissionService
from .partner_service import IPartnerService
from .dashboard_service import IDashboardService

__all__ = [
    "ICommissionService",
    "IPartnerService", 
    "IDashboardService"
]