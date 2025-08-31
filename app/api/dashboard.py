from fastapi import APIRouter
from app.services.dashboard import get_overview, get_recent_activities

router = APIRouter()

@router.get("/overview")
def fetch_overview():
    return get_overview()

@router.get("/recent-activities")
def fetch_recent_activities():
    return get_recent_activities()