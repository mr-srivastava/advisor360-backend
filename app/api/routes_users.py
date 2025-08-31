from fastapi import APIRouter
from app.services.commissions import get_commissions

router = APIRouter()

@router.get("/")
def list_commissions():
    return get_commissions()