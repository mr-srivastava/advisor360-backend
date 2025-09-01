from datetime import datetime
from app.db.supabase import get_supabase
from app.services.commissions import get_total_commissions, get_total_commissions_by_month, get_total_commissions_by_fy, get_monthly_commissions, get_commissions_with_partner, parse_commission_response
from app.utils.date_utils import parse_financial_year
from app.core.exceptions import FinancialYearNotFound, DatabaseError
import re

def get_overview():
    now = datetime.now()
    # Current and previous month/year
    current_month = now.strftime("%B")  # Example: "August"
    current_year = now.year
    current_fy = parse_financial_year(now)
    prev_month_date = datetime(now.year, now.month - 1 if now.month > 1 else 12, 1)
    prev_month = prev_month_date.strftime("%B")
    prev_year = prev_month_date.year

    # Aggregates
    total_commission = get_total_commissions()
    current_month_commission = get_total_commissions_by_month(current_month, current_year)
    prev_month_commission = get_total_commissions_by_month(prev_month, prev_year)
    fy_commission = get_total_commissions_by_fy(current_fy)


    # Growth Rate
    if prev_month_commission > 0:
        growth_rate = ((current_month_commission - prev_month_commission) / prev_month_commission) * 100
    elif current_month_commission > 0:
        growth_rate = 100
    else:
        growth_rate = 0

    stats = [
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

    return stats

def get_recent_activities():
    monthly_commissions = get_monthly_commissions() # Fetch monthly commissions
    recent_commissions = get_commissions_with_partner()[:10]  # Get the 10 most recent commissions
    return {"recent_commissions": recent_commissions,
            "monthly_commissions": monthly_commissions}

def get_available_financial_years():
    """Get all available financial years from the database"""
    try:
        supabase = get_supabase()
        response = supabase.rpc("get_financial_years").execute()
        if not response.data:
            return []
        return [row["financial_year"] for row in response.data]
    except Exception as e:
        raise DatabaseError(f"Failed to fetch financial years: {str(e)}")

def calculate_fy_metrics(selected_fy: str):
    """Calculate key metrics for a specific financial year"""
    # Validate financial year format
    if not re.match(r'^FY\d{2}-\d{2}$', selected_fy):
        raise FinancialYearNotFound(selected_fy)
    
    try:
        supabase = get_supabase()
        result = supabase.table("commissions").select("*").eq("financial_year", selected_fy).execute()
        rows = result.data or []
        fy_commissions = [parse_commission_response(row) for row in rows]

        # Filter commissions for selected FY
        current_total = sum(c.amount for c in fy_commissions)

        # Parse FY string e.g. "FY25-26"
        start = selected_fy.replace("FY", "").split("-")[0]
        prev_fy = f"FY{int(start) - 1}-{start}"
        prev_result = supabase.table("commissions").select("*").eq("financial_year", prev_fy).execute()
        prev_rows = prev_result.data or []
        prev_commissions = [parse_commission_response(row) for row in prev_rows]

        # Filter for prev year
        prev_total = sum(c.amount for c in prev_commissions)

        # YoY growth
        yoy_growth = ((current_total - prev_total) / prev_total * 100) if prev_total > 0 else 0

        return {
            "selectedFY": selected_fy,
            "currentYearTotal": current_total,
            "yoyGrowth": yoy_growth,
            "commissionCount": len(fy_commissions)
        }
    except Exception as e:
        raise DatabaseError(f"Failed to calculate FY metrics: {str(e)}")
    
def get_monthly_commissions_by_fy(financial_year: str):
    """Get monthly commission data for a specific financial year"""
    # Validate financial year format
    if not re.match(r'^FY\d{2}-\d{2}$', financial_year):
        raise FinancialYearNotFound(financial_year)
    
    try:
        supabase = get_supabase()
        response = supabase.rpc(
            "get_monthly_growth_data", {"fy": financial_year}
        ).execute()
        return response.data or []
    except Exception as e:
        raise DatabaseError(f"Failed to fetch monthly commissions: {str(e)}")

def get_entity_performance_by_fy(financial_year: str):
    """Get entity performance breakdown for a specific financial year"""
    # Validate financial year format
    if not re.match(r'^FY\d{2}-\d{2}$', financial_year):
        raise FinancialYearNotFound(financial_year)
    
    try:
        supabase = get_supabase()
        response = supabase.rpc(
            "get_entity_breakdown", {"fy": financial_year}
        ).execute()
        
        raw_data = response.data or []
        
        # Transform data to match EntityPerformanceData schema
        if raw_data and isinstance(raw_data[0], dict):
            # Check if we have the expected fields from the RPC function
            if all(key in raw_data[0] for key in ['entity_id', 'entity_name', 'total', 'percentage']):
                return raw_data
            # If we have name/value format, transform it
            elif all(key in raw_data[0] for key in ['name', 'value']):
                total_sum = sum(item.get('value', 0) for item in raw_data)
                transformed_data = []
                for i, item in enumerate(raw_data):
                    value = item.get('value', 0)
                    percentage = (value / total_sum * 100) if total_sum > 0 else 0
                    transformed_data.append({
                        'entity_id': str(i + 1),  # Generate a temporary ID
                        'entity_name': item.get('name', ''),
                        'total': float(value),
                        'percentage': float(percentage)
                    })
                return transformed_data
        
        return raw_data
    except Exception as e:
        raise DatabaseError(f"Failed to fetch entity performance: {str(e)}")