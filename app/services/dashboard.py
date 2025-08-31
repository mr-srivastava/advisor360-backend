from datetime import datetime
from app.db.supabase import get_supabase
from app.services.commissions import get_total_commissions, get_total_commissions_by_month, get_total_commissions_by_fy, get_monthly_commissions, get_commissions_with_partner, get_commissions
from app.utils.date_utils import parse_financial_year

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
    supabase = get_supabase()
    response = supabase.rpc("get_financial_years").execute()
    return [row["financial_year"] for row in response.data]

def calculate_fy_metrics(selected_fy: str):
    commissions = get_commissions()

    # Filter commissions for selected FY
    fy_commissions = [c for c in commissions if c.financialYear == selected_fy]
    current_total = sum(c.amount for c in fy_commissions if c.amount is not None)

    # Parse FY string e.g. "FY25-26"
    start = selected_fy.replace("FY", "").split("-")[0]
    prev_fy = f"FY{int(start) - 1}-{start}"

    # Filter for prev year
    prev_commissions = [c for c in commissions if c.financialYear == prev_fy]
    prev_total = sum(c.amount for c in prev_commissions if c.amount is not None)

    # YoY growth
    yoy_growth = ((current_total - prev_total) / prev_total * 100) if prev_total > 0 else 0

    return {
        "selectedFY": selected_fy,
        "currentYearTotal": current_total,
        "yoyGrowth": yoy_growth,
        "commissionCount": len(fy_commissions)
    }
    
def get_monthly_commissions_by_fy(financial_year: str):
    supabase = get_supabase()
    response = supabase.rpc(
        "get_monthly_growth_data", {"fy": financial_year}
    ).execute()
    return response.data or []

def get_entity_performance_by_fy(financial_year: str):
    supabase = get_supabase()
    response = supabase.rpc(
        "get_entity_breakdown", {"fy": financial_year}
    ).execute()
    return response.data or []