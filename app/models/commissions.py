from typing import Optional, List, Literal
from pydantic import BaseModel
from datetime import datetime

EntityType = Literal[
    "Mutual Funds",
    "Life Insurance",
    "Health Insurance",
    "General Insurance",
]

class Partner(BaseModel):
    id: str
    name: str
    entityType: EntityType
    createdAt: datetime

class Commission(BaseModel):
    id: str
    partnerId: str
    amount: float
    month: str  # Format: "August"
    year: str   # Format: "2025"
    financialYear: str  # Format: "FY25-26"
    date: datetime
    description: Optional[str] = None
    createdAt: datetime

class MonthlyAnalytics(BaseModel):
    month: str
    year: str
    total: float
    growth: float  # Percentage
    commissionCount: int

class YearlyAnalytics(BaseModel):
    financialYear: str
    total: float
    growth: float  # Percentage
    monthlyBreakdown: List[MonthlyAnalytics]