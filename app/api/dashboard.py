from fastapi import APIRouter
from app.services.dashboard import get_overview, get_recent_activities, get_available_financial_years, calculate_fy_metrics, get_monthly_commissions_by_fy, get_entity_performance_by_fy

router = APIRouter()

@router.get("/available-financial-years")
def fetch_available_financial_years():
    return get_available_financial_years()

@router.get("/key-metrics/{financial_year}")
def fetch_fy_key_metrics(financial_year: str):
    return calculate_fy_metrics(financial_year)

@router.get("/performance-metrics/{financial_year}")
def fetch_fy_performance_metrics(financial_year: str):
    monthly_growth = get_monthly_commissions_by_fy(financial_year)
    entity_performance = get_entity_performance_by_fy(financial_year)
    return {
        "monthlyGrowth": monthly_growth,
        "entityPerformance": entity_performance
    }

@router.get("/overview")
def fetch_overview():
    return get_overview()

@router.get("/recent-activities")
def fetch_recent_activities():
    return get_recent_activities()