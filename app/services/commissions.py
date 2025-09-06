"""
Commission service implementation providing business logic for commission operations.
"""

from typing import List, Dict, Optional
from datetime import datetime, date
from .interfaces.commission_service import ICommissionService
from ..repositories.interfaces.commission_repository import ICommissionRepository
from ..repositories.interfaces.partner_repository import IPartnerRepository
from ..domain.commission import Commission
from ..domain.value_objects.money import Money
from ..domain.value_objects.financial_year import FinancialYear
from ..core.exceptions import CommissionNotFound, PartnerNotFound, ValidationError, DomainException
from ..utils.date_utils import format_month_year


class CommissionService(ICommissionService):
    """
    Commission service implementation providing business logic for commission operations.
    
    Coordinates between commission and partner repositories to provide high-level
    business functionality for commission management.
    """
    
    def __init__(self, 
                 commission_repository: ICommissionRepository,
                 partner_repository: IPartnerRepository):
        self._commission_repo = commission_repository
        self._partner_repo = partner_repository
    
    async def get_all_commissions(self) -> List[Commission]:
        """Retrieve all commissions in the system."""
        try:
            return await self._commission_repo.get_all()
        except Exception as e:
            raise ServiceError(f"Failed to retrieve commissions: {str(e)}")
    
    async def get_commission_by_id(self, commission_id: str) -> Commission:
        """Retrieve a specific commission by ID."""
        try:
            commission = await self._commission_repo.get_by_id(commission_id)
            if not commission:
                raise CommissionNotFound(commission_id)
            return commission
        except CommissionNotFound:
            raise
        except Exception as e:
            raise ServiceError(f"Failed to retrieve commission: {str(e)}")
    
    async def get_commissions_by_partner(self, partner_id: str) -> List[Commission]:
        """Retrieve all commissions for a specific partner."""
        try:
            # Verify partner exists
            partner = await self._partner_repo.get_by_id(partner_id)
            if not partner:
                raise PartnerNotFound(partner_id)
            
            return await self._commission_repo.get_by_partner_id(partner_id)
        except PartnerNotFound:
            raise
        except Exception as e:
            raise ServiceError(f"Failed to retrieve commissions for partner: {str(e)}")
    
    async def get_commissions_by_financial_year(self, financial_year: str) -> List[Commission]:
        """Retrieve all commissions for a specific financial year."""
        try:
            fy = FinancialYear.from_string(financial_year)
            return await self._commission_repo.get_by_financial_year(fy)
        except Exception as e:
            raise ServiceError(f"Failed to retrieve commissions for financial year: {str(e)}")
    
    async def get_commissions_with_partners(self) -> List[Dict]:
        """Retrieve all commissions with their associated partner information."""
        try:
            commissions = await self._commission_repo.get_all()
            partners = await self._partner_repo.get_all()
            
            # Create partner lookup
            partner_lookup = {p.id: p for p in partners}
            
            result = []
            for commission in commissions:
                partner = partner_lookup.get(commission.partner_id)
                commission_dict = commission.to_dict()
                commission_dict["partner"] = partner.to_dict() if partner else None
                result.append(commission_dict)
            
            return result
        except Exception as e:
            raise ServiceError(f"Failed to retrieve commissions with partners: {str(e)}")
    
    async def create_commission(self, partner_id: str, amount: float, 
                              transaction_date: date, description: Optional[str] = None) -> Commission:
        """Create a new commission."""
        try:
            # Verify partner exists
            partner = await self._partner_repo.get_by_id(partner_id)
            if not partner:
                raise PartnerNotFound(partner_id)
            
            # Create domain objects
            money = Money.from_float(amount)
            commission = Commission.create_new(partner_id, money, transaction_date, description)
            
            # Save to repository
            return await self._commission_repo.create(commission)
        except (PartnerNotFound, ValidationError):
            raise
        except Exception as e:
            raise ServiceError(f"Failed to create commission: {str(e)}")
    
    async def update_commission(self, commission_id: str, amount: Optional[float] = None,
                              description: Optional[str] = None) -> Commission:
        """Update an existing commission."""
        try:
            # Get existing commission
            commission = await self._commission_repo.get_by_id(commission_id)
            if not commission:
                raise CommissionNotFound(commission_id)
            
            # Apply updates
            updated_commission = commission
            if amount is not None:
                money = Money.from_float(amount)
                updated_commission = updated_commission.update_amount(money)
            
            if description is not None:
                updated_commission = updated_commission.update_description(description)
            
            # Save changes
            return await self._commission_repo.update(commission_id, updated_commission)
        except (CommissionNotFound, ValidationError):
            raise
        except Exception as e:
            raise ServiceError(f"Failed to update commission: {str(e)}")
    
    async def delete_commission(self, commission_id: str) -> bool:
        """Delete a commission."""
        try:
            # Verify commission exists
            commission = await self._commission_repo.get_by_id(commission_id)
            if not commission:
                raise CommissionNotFound(commission_id)
            
            return await self._commission_repo.delete(commission_id)
        except CommissionNotFound:
            raise
        except Exception as e:
            raise ServiceError(f"Failed to delete commission: {str(e)}")
    
    async def get_total_commissions(self) -> float:
        """Get total commission amount across all time."""
        try:
            commissions = await self._commission_repo.get_all()
            return sum(c.amount.to_float() for c in commissions)
        except Exception as e:
            raise ServiceError(f"Failed to calculate total commissions: {str(e)}")
    
    async def get_total_commissions_by_month(self, month: str, year: int) -> float:
        """Get total commission amount for a specific month and year."""
        try:
            month_num = datetime.strptime(month, "%B").month
            commissions = await self._commission_repo.get_by_month_year(month_num, year)
            return sum(c.amount.to_float() for c in commissions)
        except Exception as e:
            raise ServiceError(f"Failed to calculate monthly commissions: {str(e)}")
    
    async def get_total_commissions_by_financial_year(self, financial_year: str) -> float:
        """Get total commission amount for a specific financial year."""
        try:
            fy = FinancialYear.from_string(financial_year)
            return await self._commission_repo.get_total_amount_by_financial_year(fy)
        except Exception as e:
            raise ServiceError(f"Failed to calculate FY commissions: {str(e)}")
    
    async def get_monthly_analytics(self) -> List[Dict]:
        """Get monthly commission analytics for the last 6 months."""
        try:
            commissions = await self._commission_repo.get_all()
            monthly_data = {}
            
            # Aggregate by month
            for commission in commissions:
                month = commission.get_month_name()
                year = commission.get_year()
                key = format_month_year(month, str(year))
                
                if key not in monthly_data:
                    monthly_data[key] = {"month": key, "total": 0, "count": 0}
                
                monthly_data[key]["total"] += commission.amount.to_float()
                monthly_data[key]["count"] += 1
            
            # Convert to list and sort
            monthly_data_list = list(monthly_data.values())
            monthly_data_list.sort(
                key=lambda x: datetime.strptime(x["month"], "%B %Y")
            )
            
            # Return last 6 months
            return monthly_data_list[-6:]
        except Exception as e:
            raise ServiceError(f"Failed to generate monthly analytics: {str(e)}")
    
    async def get_recent_commissions(self, limit: int = 10) -> List[Commission]:
        """Get the most recent commissions."""
        try:
            return await self._commission_repo.get_recent_commissions(limit)
        except Exception as e:
            raise ServiceError(f"Failed to retrieve recent commissions: {str(e)}")
    
    async def search_commissions(self, search_term: str) -> List[Commission]:
        """Search commissions by description."""
        try:
            return await self._commission_repo.search_by_description(search_term)
        except Exception as e:
            raise ServiceError(f"Failed to search commissions: {str(e)}")