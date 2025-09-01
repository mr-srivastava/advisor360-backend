from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import commissions, partners, dashboard
from app.core.error_handlers import (
    advisor360_exception_handler,
    financial_year_not_found_handler,
    partner_not_found_handler,
    commission_not_found_handler,
    invalid_financial_year_handler,
    database_error_handler
)
from app.core.exceptions import (
    Advisor360Exception,
    FinancialYearNotFound,
    PartnerNotFound,
    CommissionNotFound,
    InvalidFinancialYearFormat,
    DatabaseError
)

app = FastAPI(
    title="Advisor360 API",
    description="Financial advisory platform API for tracking commissions and partner relationships",
    version="1.0.0"
)

# Allow origins (React dev server, etc.)
origins = [
    "https://advisor360.vercel.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"],          # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],          # Allow all headers
)

# Add exception handlers
app.add_exception_handler(Advisor360Exception, advisor360_exception_handler)
app.add_exception_handler(FinancialYearNotFound, financial_year_not_found_handler)
app.add_exception_handler(PartnerNotFound, partner_not_found_handler)
app.add_exception_handler(CommissionNotFound, commission_not_found_handler)
app.add_exception_handler(InvalidFinancialYearFormat, invalid_financial_year_handler)
app.add_exception_handler(DatabaseError, database_error_handler)

# include routers
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
app.include_router(partners.router, prefix="/partners", tags=["partners"])
app.include_router(commissions.router, prefix="/commissions", tags=["commissions"])

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Advisor360 API"}