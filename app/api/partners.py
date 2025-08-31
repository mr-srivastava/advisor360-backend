from fastapi import APIRouter
from app.services.partners import get_partners, get_entity_types

router = APIRouter()

@router.get("/")
def read_partners():
    return get_partners()

@router.get("/types")
def read_partner_types():
    return get_entity_types()