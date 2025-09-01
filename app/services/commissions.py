from app.db.supabase import get_supabase
from app.services.partners import get_entities
from app.utils.date_utils import parse_financial_year
from app.models.commissions import Commission
from app.models.api.responses import CommissionResponse
from app.core.exceptions import CommissionNotFound, DatabaseError
from datetime import datetime, date
from typing import List
from app.utils.date_utils import format_month_year


def get_transactions():
    """Get all transactions from the database"""
    try:
        supabase = get_supabase()
        data = supabase.table("entity_transactions").select("*").order('month', desc=True).execute()
        return data.data or []
    except Exception as e:
        raise DatabaseError(f"Failed to fetch transactions: {str(e)}")

def get_total_commissions() -> float:
    """Get total commissions across all time"""
    try:
        supabase = get_supabase()
        response = supabase.rpc("get_total_commissions").execute()
        return response.data or 0.0
    except Exception as e:
        raise DatabaseError(f"Failed to fetch total commissions: {str(e)}")

def get_total_commissions_by_month(month: str, year: int) -> float:
    """Get total commissions for a specific month and year"""
    try:
        supabase = get_supabase()
        month_num = datetime.strptime(month, "%B").month
        response = supabase.rpc(
            "get_total_commissions_by_month", {"y": year, "m": month_num}
        ).execute()
        return response.data or 0.0
    except Exception as e:
        raise DatabaseError(f"Failed to fetch monthly commissions: {str(e)}")

def get_total_commissions_by_fy(financial_year: str) -> float:
    """Get total commissions for a specific financial year"""
    try:
        supabase = get_supabase()
        response = supabase.rpc(
            "get_total_commissions_by_fy", {"fy": financial_year}
        ).execute()
        return response.data or 0.0
    except Exception as e:
        raise DatabaseError(f"Failed to fetch FY commissions: {str(e)}")

def parse_commission_response(row: dict) -> CommissionResponse:
    try:
        return CommissionResponse(
        id=row.get("id"),
        partnerId=row.get("partner_id"),
        month=row.get("month_name"),
        financialYear=row.get("financial_year"),
        createdAt=row.get("created_at"),
        updatedAt=row.get("updated_at"),
        partner=row.get("partner"),
        amount=row.get("amount"),
        year=row.get("year"),
        date=row.get("date"),
        description=row.get("description"))
    except Exception as e:
        raise DatabaseError(f"Failed to parse commission response: {str(e)}")


def get_commissions() -> List[CommissionResponse]:
    """Get all commissions with proper formatting"""
    try:
        supabase = get_supabase()
        result = supabase.table("commissions").select("*").execute()
        rows = result.data or []
        formatted: List[CommissionResponse] = []
        for row in rows:
            commission = parse_commission_response(row)
            formatted.append(commission)

        return formatted
    except Exception as e:
        raise DatabaseError(f"Failed to fetch commissions: {str(e)}")

def get_commissions_with_partner() -> List[dict]:
    """Get commissions with partner information"""
    try:
        commissions = get_commissions()
        # Since get_commissions now returns CommissionResponse objects with partner info,
        # we can just convert them to dicts
        result = []
        for commission in commissions:
            result.append(commission.model_dump())

        return result
    except Exception as e:
        raise DatabaseError(f"Failed to fetch commissions with partners: {str(e)}")

def get_monthly_commissions():
    """Get monthly commission summaries"""
    try:
        # Fetch commissions from Supabase
        commissions = get_commissions()
        monthly_data = {}

        # Aggregate like your TS logic
        for commission in commissions:
            month = commission.month
            year = commission.year
            key = format_month_year(month, year)

            if key not in monthly_data:
                monthly_data[key] = {"month": key, "total": 0, "count": 0}

            monthly_data[key]["total"] += commission.amount
            monthly_data[key]["count"] += 1

        # Convert to list + sort
        monthly_data_list = list(monthly_data.values())
        monthly_data_list.sort(
            key=lambda x: datetime.strptime(x["month"], "%B %Y")
        )

        # Return last 6 months
        return monthly_data_list[-6:]
    except Exception as e:
        raise DatabaseError(f"Failed to fetch monthly commissions: {str(e)}")

def get_commission_by_id(commission_id: str) -> CommissionResponse:
    """Get a specific commission by ID"""
    try:
        commissions = get_commissions()
        commission = next((c for c in commissions if c.id == commission_id), None)
        
        if not commission:
            raise CommissionNotFound(commission_id)
        
        return commission
    except CommissionNotFound:
        raise
    except Exception as e:
        raise DatabaseError(f"Failed to fetch commission: {str(e)}")