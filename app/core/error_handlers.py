"""
Error handlers for FastAPI application
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.exceptions import (
    Advisor360Exception,
    FinancialYearNotFound,
    PartnerNotFound,
    CommissionNotFound,
    InvalidFinancialYearFormat,
    DatabaseError
)

async def advisor360_exception_handler(request: Request, exc: Advisor360Exception):
    """Handle custom Advisor360 exceptions"""
    return JSONResponse(
        status_code=400,
        content={
            "detail": str(exc),
            "type": exc.__class__.__name__
        }
    )

async def financial_year_not_found_handler(request: Request, exc: FinancialYearNotFound):
    """Handle financial year not found exceptions"""
    return JSONResponse(
        status_code=404,
        content={
            "detail": f"Financial year {exc.financial_year} not found",
            "type": "FinancialYearNotFound",
            "financial_year": exc.financial_year
        }
    )

async def partner_not_found_handler(request: Request, exc: PartnerNotFound):
    """Handle partner not found exceptions"""
    return JSONResponse(
        status_code=404,
        content={
            "detail": f"Partner with ID {exc.partner_id} not found",
            "type": "PartnerNotFound",
            "partner_id": exc.partner_id
        }
    )

async def commission_not_found_handler(request: Request, exc: CommissionNotFound):
    """Handle commission not found exceptions"""
    return JSONResponse(
        status_code=404,
        content={
            "detail": f"Commission with ID {exc.commission_id} not found",
            "type": "CommissionNotFound",
            "commission_id": exc.commission_id
        }
    )

async def invalid_financial_year_handler(request: Request, exc: InvalidFinancialYearFormat):
    """Handle invalid financial year format exceptions"""
    return JSONResponse(
        status_code=422,
        content={
            "detail": f"Invalid financial year format: {exc.financial_year}. Expected format: FY25-26",
            "type": "InvalidFinancialYearFormat",
            "financial_year": exc.financial_year
        }
    )

async def database_error_handler(request: Request, exc: DatabaseError):
    """Handle database error exceptions"""
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "type": "DatabaseError"
        }
    )
