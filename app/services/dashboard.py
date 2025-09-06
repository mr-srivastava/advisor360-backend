"""
Dashboard service implementation providing analytics and reporting operations.
"""

from typing import List, Dict, Any
from datetime import datetime, date
from .interfaces.dashboard_service import IDashboardService
from .interfaces.commission_service import ICommissionService
from .interfaces.partner_service import IPartnerService
from ..repositories.interfaces.commission_repository import ICommissionRepository
from ..domain.value_objects.financial_year import FinancialYear
from ..core.exceptions import FinancialYearError, DomainException
from ..utils.date_utils import parse_financial_year, format_month_year
import re

class DashboardService(IDashboardService):
    """
    Dashboard service implementation providing analytics and reporting operations.
    
    Coordinates between commission and partner services to provide high-level
    analytics and reporting functionality for the dashboard.
    """
    
    def __init__(self, 
                 commission_service: ICommissionService,
                 partner_service: IPartnerService,
                 commission_repository: ICommissionRepository):
        self._commission_service = commission_service
        self._partner_service = partner_service
        self._commission_repo = commission_repository
    
    async def get_overview_statistics(self) -> List[Dict[str, Any]]:
        """Get overview statistics for the dashboard."""
        try:
            now = datetime.now()
            current_month = now.strftime("%B")
            current_year = now.year
            current_fy = parse_financial_year(now)
            
            # Calculate previous month
            prev_month_date = datetime(now.year, now.month - 1 if now.month > 1 else 12, 1)
            prev_month = prev_month_date.strftime("%B")
            prev_year = prev_month_date.year
            
            # Get totals
            total_commission = await self._commission_service.get_total_commissions()
            current_month_commission = await self._commission_service.get_total_commissions_by_month(current_month, current_year)
            prev_month_commission = await self._commission_service.get_total_commissions_by_month(prev_month, prev_year)
            fy_commission = await self._commission_service.get_total_commissions_by_financial_year(current_fy)
            
            # Calculate growth rate
            if prev_month_commission > 0:
                growth_rate = ((current_month_commission - prev_month_commission) / prev_month_commission) * 100
            elif current_month_commission > 0:
                growth_rate = 100
            else:
                growth_rate = 0
            
            return [
                {
                    "id": "1",
                    "title": "Total Commission",
                    "value": total_commission,
                    "subtitle": "All time earnings",
                    "icon": "dollarSign",
                },
                {
                    "id": "2",
                    "title": f'{current_month} Commission',
                    "value": current_month_commission,
                    "subtitle": f"Compared to {prev_month}",
                    "icon": "target",
                },
                {
                    "id": "3",
                    "title": f'{current_fy} Commission',
                    "value": fy_commission,
                    "subtitle": "Current financial year",
                    "icon": "building2",
                },
                {
                    "id": "4",
                    "title": "Growth Rate",
                    "value": f"{growth_rate:.1f}%",
                    "subtitle": f"vs {prev_month}",
                    "icon": "trendingUp",
                    "trend": {
                        "value": f"{growth_rate:.1f}%",
                        "isPositive": growth_rate >= 0,
                    },
                },
            ]
        except Exception as e:
            raise ServiceError(f"Failed to get overview statistics: {str(e)}")
    
    async def get_recent_activities(self) -> Dict[str, Any]:
        """Get recent activities including recent commissions and monthly data."""
        try:
            monthly_commissions = await self._commission_service.get_monthly_analytics()
            recent_commissions_data = await self._commission_service.get_commissions_with_partners()
            recent_commissions = recent_commissions_data[:10]  # Get the 10 most recent
            
            return {
                "recent_commissions": recent_commissions,
                "monthly_commissions": monthly_commissions
            }
        except Exception as e:
            raise ServiceError(f"Failed to get recent activities: {str(e)}")
    
    async def get_available_financial_years(self) -> List[str]:
        """Get all available financial years from the system."""
        try:
            commissions = await self._commission_service.get_all_commissions()
            financial_years = set()
            
            for commission in commissions:
                financial_years.add(commission.financial_year.to_string("short"))
            
            return sorted(list(financial_years), reverse=True)
        except Exception as e:
            raise ServiceError(f"Failed to get available financial years: {str(e)}")
    
    async def calculate_financial_year_metrics(self, financial_year: str) -> Dict[str, Any]:
        """Calculate key metrics for a specific financial year."""
        try:
            # Validate financial year format
            if not re.match(r'^FY\d{2}-\d{2}$', financial_year):
                raise FinancialYearNotFound(financial_year)
            
            # Get current FY commissions
            current_commissions = await self._commission_service.get_commissions_by_financial_year(financial_year)
            current_total = sum(c.amount.to_float() for c in current_commissions)
            
            # Calculate previous FY
            start_year = financial_year.replace("FY", "").split("-")[0]
            prev_fy = f"FY{int(start_year) - 1:02d}-{start_year}"
            
            # Get previous FY commissions
            try:
                prev_commissions = await self._commission_service.get_commissions_by_financial_year(prev_fy)
                prev_total = sum(c.amount.to_float() for c in prev_commissions)
            except:
                prev_total = 0
            
            # Calculate YoY growth
            yoy_growth = ((current_total - prev_total) / prev_total * 100) if prev_total > 0 else 0
            
            return {
                "selectedFY": financial_year,
                "currentYearTotal": current_total,
                "yoyGrowth": yoy_growth,
                "commissionCount": len(current_commissions)
            }
        except FinancialYearNotFound:
            raise
        except Exception as e:
            raise ServiceError(f"Failed to calculate FY metrics: {str(e)}")
    
    async def get_monthly_commissions_by_financial_year(self, financial_year: str) -> List[Dict[str, Any]]:
        """Get monthly commission breakdown for a specific financial year."""
        try:
            # Validate financial year format
            if not re.match(r'^FY\d{2}-\d{2}$', financial_year):
                raise FinancialYearNotFound(financial_year)
            
            commissions = await self._commission_service.get_commissions_by_financial_year(financial_year)
            monthly_data = {}
            
            # Aggregate by month
            for commission in commissions:
                month_key = f"{commission.get_month_name()} {commission.get_year()}"
                
                if month_key not in monthly_data:
                    monthly_data[month_key] = {
                        "month": commission.get_month_name(),
                        "year": commission.get_year(),
                        "total": 0,
                        "count": 0
                    }
                
                monthly_data[month_key]["total"] += commission.amount.to_float()
                monthly_data[month_key]["count"] += 1
            
            # Convert to list and sort
            result = list(monthly_data.values())
            result.sort(key=lambda x: datetime.strptime(f"{x['month']} {x['year']}", "%B %Y"))
            
            return result
        except FinancialYearNotFound:
            raise
        except Exception as e:
            raise ServiceError(f"Failed to get monthly commissions: {str(e)}")
    
    async def get_entity_performance_by_financial_year(self, financial_year: str) -> List[Dict[str, Any]]:
        """Get entity performance breakdown for a specific financial year."""
        try:
            # Validate financial year format
            if not re.match(r'^FY\d{2}-\d{2}$', financial_year):
                raise FinancialYearNotFound(financial_year)
            
            commissions = await self._commission_service.get_commissions_by_financial_year(financial_year)
            partners = await self._partner_service.get_all_partners()
            
            # Create partner lookup
            partner_lookup = {p.id: p for p in partners}
            
            # Aggregate by entity type
            entity_totals = {}
            total_amount = 0
            
            for commission in commissions:
                partner = partner_lookup.get(commission.partner_id)
                if partner:
                    entity_type = partner.entity_type.value
                    amount = commission.amount.to_float()
                    
                    if entity_type not in entity_totals:
                        entity_totals[entity_type] = 0
                    
                    entity_totals[entity_type] += amount
                    total_amount += amount
            
            # Calculate percentages and format result
            result = []
            for i, (entity_type, total) in enumerate(entity_totals.items()):
                percentage = (total / total_amount * 100) if total_amount > 0 else 0
                result.append({
                    "entity_id": str(i + 1),
                    "entity_name": entity_type,
                    "total": total,
                    "percentage": percentage
                })
            
            return result
        except FinancialYearNotFound:
            raise
        except Exception as e:
            raise ServiceError(f"Failed to get entity performance: {str(e)}")
    
    async def get_growth_analytics(self, financial_year: str) -> Dict[str, Any]:
        """Get growth analytics comparing current and previous financial years."""
        try:
            metrics = await self.calculate_financial_year_metrics(financial_year)
            monthly_data = await self.get_monthly_commissions_by_financial_year(financial_year)
            
            return {
                "financial_year": financial_year,
                "total_commission": metrics["currentYearTotal"],
                "yoy_growth": metrics["yoyGrowth"],
                "commission_count": metrics["commissionCount"],
                "monthly_breakdown": monthly_data
            }
        except Exception as e:
            raise ServiceError(f"Failed to get growth analytics: {str(e)}")
    
    async def get_commission_trends(self, months: int = 12) -> List[Dict[str, Any]]:
        """Get commission trends over the specified number of months."""
        try:
            commissions = await self._commission_service.get_all_commissions()
            
            # Get recent months data
            monthly_data = {}
            for commission in commissions:
                month_key = f"{commission.get_month_name()} {commission.get_year()}"
                
                if month_key not in monthly_data:
                    monthly_data[month_key] = {
                        "month": commission.get_month_name(),
                        "year": commission.get_year(),
                        "total": 0,
                        "count": 0
                    }
                
                monthly_data[month_key]["total"] += commission.amount.to_float()
                monthly_data[month_key]["count"] += 1
            
            # Sort and limit to requested months
            result = list(monthly_data.values())
            result.sort(key=lambda x: datetime.strptime(f"{x['month']} {x['year']}", "%B %Y"), reverse=True)
            
            return result[:months]
        except Exception as e:
            raise ServiceError(f"Failed to get commission trends: {str(e)}")
    
    async def get_partner_performance_summary(self) -> List[Dict[str, Any]]:
        """Get performance summary for all partners."""
        try:
            partners = await self._partner_service.get_all_partners()
            result = []
            
            for partner in partners:
                commissions = await self._commission_service.get_commissions_by_partner(partner.id)
                total_amount = sum(c.amount.to_float() for c in commissions)
                
                result.append({
                    "partner_id": partner.id,
                    "partner_name": partner.name,
                    "entity_type": partner.entity_type.value,
                    "total_commission": total_amount,
                    "commission_count": len(commissions)
                })
            
            # Sort by total commission descending
            result.sort(key=lambda x: x["total_commission"], reverse=True)
            
            return result
        except Exception as e:
            raise ServiceError(f"Failed to get partner performance summary: {str(e)}")
    
    async def get_quarterly_breakdown(self, financial_year: str) -> List[Dict[str, Any]]:
        """Get quarterly commission breakdown for a financial year."""
        try:
            # Validate financial year format
            if not re.match(r'^FY\d{2}-\d{2}$', financial_year):
                raise FinancialYearNotFound(financial_year)
            
            commissions = await self._commission_service.get_commissions_by_financial_year(financial_year)
            quarterly_data = {1: 0, 2: 0, 3: 0, 4: 0}
            
            # Aggregate by quarter
            for commission in commissions:
                quarter = commission.get_quarter()
                quarterly_data[quarter] += commission.amount.to_float()
            
            # Format result
            result = []
            for quarter, total in quarterly_data.items():
                result.append({
                    "quarter": f"Q{quarter}",
                    "total": total,
                    "financial_year": financial_year
                })
            
            return result
        except FinancialYearNotFound:
            raise
        except Exception as e:
            raise ServiceError(f"Failed to get quarterly breakdown: {str(e)}")