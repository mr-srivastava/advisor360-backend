from fastapi import APIRouter, HTTPException, Query

from ..core.exceptions import DomainException, FinancialYearError
from .dependencies import DashboardServiceDep
from .dtos.dashboard_dtos import (
    DashboardMapper,
    DashboardOverviewData,
    DashboardOverviewResponse,
    FinancialYearPathParam,
    FinancialYearsData,
    FinancialYearsResponse,
    FYMetricsData,
    FYMetricsResponse,
    PerformanceMetricsData,
    PerformanceMetricsResponse,
    RecentActivityData,
    RecentActivityResponse,
)

router = APIRouter()


@router.get(
    "/available-financial-years",
    response_model=FinancialYearsResponse,
    summary="Get available financial years",
    description="Returns a list of all available financial years in the system",
)
async def get_available_financial_years(dashboard_service: DashboardServiceDep):
    """Get all available financial years"""
    try:
        financial_years = await dashboard_service.get_available_financial_years()

        return FinancialYearsResponse(
            data=FinancialYearsData(financial_years=financial_years),
            message="Financial years retrieved successfully",
        )
    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch financial years: {str(e)}"
        )


@router.get(
    "/key-metrics/{financial_year}",
    response_model=FYMetricsResponse,
    summary="Get key metrics for financial year",
    description="Returns key metrics including total, growth, and commission count for a specific financial year",
)
async def get_fy_key_metrics(
    financial_year: str, dashboard_service: DashboardServiceDep
):
    """Get key metrics for a specific financial year"""
    try:
        # Validate financial year format
        fy_param = FinancialYearPathParam(financial_year=financial_year)

        metrics = await dashboard_service.calculate_financial_year_metrics(
            fy_param.financial_year
        )

        return FYMetricsResponse(
            data=FYMetricsData(
                selected_fy=metrics["selectedFY"],
                current_year_total=metrics["currentYearTotal"],
                yoy_growth=metrics["yoyGrowth"],
                commission_count=metrics["commissionCount"],
            ),
            message="Key metrics retrieved successfully",
        )
    except FinancialYearError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch key metrics: {str(e)}"
        )


@router.get(
    "/performance-metrics/{financial_year}",
    response_model=PerformanceMetricsResponse,
    summary="Get performance metrics for financial year",
    description="Returns monthly growth data and entity performance breakdown for a specific financial year",
)
async def get_fy_performance_metrics(
    financial_year: str, dashboard_service: DashboardServiceDep
):
    """Get performance metrics for a specific financial year"""
    try:
        # Validate financial year format
        fy_param = FinancialYearPathParam(financial_year=financial_year)

        monthly_growth = (
            await dashboard_service.get_monthly_commissions_by_financial_year(
                fy_param.financial_year
            )
        )
        entity_performance = (
            await dashboard_service.get_entity_performance_by_financial_year(
                fy_param.financial_year
            )
        )

        return PerformanceMetricsResponse(
            data=PerformanceMetricsData(
                monthly_growth=monthly_growth, entity_performance=entity_performance
            ),
            message="Performance metrics retrieved successfully",
        )
    except FinancialYearError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch performance metrics: {str(e)}"
        )


@router.get(
    "/overview",
    response_model=DashboardOverviewResponse,
    summary="Get dashboard overview",
    description="Returns overview statistics including total commissions, monthly data, and growth rates",
)
async def get_overview(dashboard_service: DashboardServiceDep):
    """Get dashboard overview statistics"""
    try:
        stats = await dashboard_service.get_overview_statistics()

        # Convert to stat cards format
        stat_cards = []
        for stat in stats:
            trend_data = None
            if "trend" in stat and stat["trend"]:
                trend_data = DashboardMapper.create_trend_data(
                    float(stat["trend"]["value"].replace("%", "").replace("+", ""))
                )

            stat_card = DashboardMapper.create_stat_card(
                id=stat["id"],
                title=stat["title"],
                value=(
                    DashboardMapper.format_currency(stat["value"])
                    if isinstance(stat["value"], (int, float))
                    else str(stat["value"])
                ),
                subtitle=stat["subtitle"],
                icon=stat["icon"],
                trend=trend_data,
            )
            stat_cards.append(stat_card)

        overview_data = DashboardOverviewData(stats=stat_cards)

        return DashboardOverviewResponse(
            data=overview_data, message="Dashboard overview retrieved successfully"
        )
    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch dashboard overview: {str(e)}"
        )


@router.get(
    "/recent-activities",
    response_model=RecentActivityResponse,
    summary="Get recent activities",
    description="Returns recent commission activities and monthly summaries",
)
async def get_recent_activities(dashboard_service: DashboardServiceDep):
    """Get recent activities"""
    try:
        activities = await dashboard_service.get_recent_activities()

        return RecentActivityResponse(
            data=RecentActivityData(
                recent_commissions=activities["recent_commissions"],
                monthly_commissions=activities["monthly_commissions"],
            ),
            message="Recent activities retrieved successfully",
        )
    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch recent activities: {str(e)}"
        )


@router.get(
    "/analytics/{financial_year}",
    summary="Get comprehensive analytics for financial year",
    description="Returns comprehensive analytics including trends, comparisons, and breakdowns",
)
async def get_analytics(
    financial_year: str,
    dashboard_service: DashboardServiceDep,
    include_quarterly: bool = Query(True, description="Include quarterly breakdown"),
    include_trends: bool = Query(True, description="Include trend analysis"),
):
    """Get comprehensive analytics for a financial year"""
    try:
        # Validate financial year format
        fy_param = FinancialYearPathParam(financial_year=financial_year)

        analytics = await dashboard_service.get_growth_analytics(
            fy_param.financial_year
        )

        result = {
            "financial_year": analytics["financial_year"],
            "total_commission": analytics["total_commission"],
            "yoy_growth": analytics["yoy_growth"],
            "commission_count": analytics["commission_count"],
            "monthly_breakdown": analytics["monthly_breakdown"],
        }

        if include_quarterly:
            quarterly_data = await dashboard_service.get_quarterly_breakdown(
                fy_param.financial_year
            )
            result["quarterly_breakdown"] = quarterly_data

        if include_trends:
            trends = await dashboard_service.get_commission_trends(12)
            result["trends"] = trends

        return {
            "success": True,
            "data": result,
            "message": "Analytics retrieved successfully",
        }
    except FinancialYearError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch analytics: {str(e)}"
        )
