from datetime import datetime
from app.services.commissions import get_commissions,get_total_commissions, get_total_commissions_by_month, get_total_commissions_by_fy, get_monthly_commissions, get_commissions_with_partner
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