"""
FastAPI dependencies for dependency injection.

This module provides FastAPI dependency functions that integrate with the
dependency injection container to provide services to API routes.
"""

from fastapi import Depends
from typing import Annotated

from ..core.container import get_container
from ..services.interfaces.commission_service import ICommissionService
from ..services.interfaces.partner_service import IPartnerService
from ..services.interfaces.dashboard_service import IDashboardService


def get_commission_service() -> ICommissionService:
    """Get commission service from DI container."""
    container = get_container()
    return container.get(ICommissionService)


def get_partner_service() -> IPartnerService:
    """Get partner service from DI container."""
    container = get_container()
    return container.get(IPartnerService)


def get_dashboard_service() -> IDashboardService:
    """Get dashboard service from DI container."""
    container = get_container()
    return container.get(IDashboardService)


# Type aliases for cleaner dependency injection
CommissionServiceDep = Annotated[ICommissionService, Depends(get_commission_service)]
PartnerServiceDep = Annotated[IPartnerService, Depends(get_partner_service)]
DashboardServiceDep = Annotated[IDashboardService, Depends(get_dashboard_service)]