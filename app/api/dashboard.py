from fastapi import APIRouter, Depends, HTTPException
from app.services.dashboard import (
    get_overview, 
    get_recent_activities, 
    get_available_financial_years, 
    calculate_fy_metrics, 
    get_monthly_commissions_by_fy, 
    get_entity_performance_by_fy
)
from app.models.api.requests import FinancialYearPath, DashboardQuery
from app.models.api.responses import (
    DashboardOverviewResponse,
    FYMetricsResponse,
    FYMetricsData,
    PerformanceMetricsResponse,
    PerformanceMetricsData,
    RecentActivityResponse,
    RecentActivityData,
    FinancialYearsResponse,
    FinancialYearsData
)
from app.core.exceptions import FinancialYearNotFound, InvalidFinancialYearFormat

router = APIRouter()

@router.get("/available-financial-years", 
           response_model=FinancialYearsResponse,
           summary="Get available financial years",
           description="Returns a list of all available financial years in the system")
def fetch_available_financial_years():
    """Get all available financial years"""
    try:
        financial_years = get_available_financial_years()
        return FinancialYearsResponse(
            data=FinancialYearsData(financial_years=financial_years),
            message="Financial years retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch financial years: {str(e)}")

@router.get("/key-metrics/{financial_year}", 
           response_model=FYMetricsResponse,
           summary="Get key metrics for financial year",
           description="Returns key metrics including total, growth, and commission count for a specific financial year")
def fetch_fy_key_metrics(financial_year: FinancialYearPath = Depends()):
    """Get key metrics for a specific financial year"""
    try:
        metrics = calculate_fy_metrics(financial_year.financial_year)
        return FYMetricsResponse(
            data=FYMetricsData(
                selectedFY=metrics["selectedFY"],
                currentYearTotal=metrics["currentYearTotal"],
                yoyGrowth=metrics["yoyGrowth"],
                commissionCount=metrics["commissionCount"]
            ),
            message="Key metrics retrieved successfully"
        )
    except FinancialYearNotFound:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch key metrics: {str(e)}")

@router.get("/performance-metrics/{financial_year}",
           response_model=PerformanceMetricsResponse,
           summary="Get performance metrics for financial year",
           description="Returns monthly growth data and entity performance breakdown for a specific financial year")
def fetch_fy_performance_metrics(financial_year: FinancialYearPath = Depends()):
    """Get performance metrics for a specific financial year"""
    try:
        monthly_growth = get_monthly_commissions_by_fy(financial_year.financial_year)
        entity_performance = get_entity_performance_by_fy(financial_year.financial_year)
        return PerformanceMetricsResponse(
            data=PerformanceMetricsData(
                monthlyGrowth=monthly_growth,
                entityPerformance=entity_performance
            ),
            message="Performance metrics retrieved successfully"
        )
    except FinancialYearNotFound:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch performance metrics: {str(e)}")

@router.get("/overview",
           response_model=DashboardOverviewResponse,
           summary="Get dashboard overview",
           description="Returns overview statistics including total commissions, monthly data, and growth rates")
def fetch_overview():
    """Get dashboard overview statistics"""
    try:
        stats = get_overview()
        return DashboardOverviewResponse(
            data={"stats": stats},
            message="Dashboard overview retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard overview: {str(e)}")

@router.get("/recent-activities",
           response_model=RecentActivityResponse,
           summary="Get recent activities",
           description="Returns recent commission activities and monthly summaries")
def fetch_recent_activities():
    """Get recent activities"""
    try:
        activities = get_recent_activities()
        return RecentActivityResponse(
            data=RecentActivityData(
                recent_commissions=activities["recent_commissions"],
                monthly_commissions=activities["monthly_commissions"]
            ),
            message="Recent activities retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch recent activities: {str(e)}")