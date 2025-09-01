from fastapi import APIRouter, Depends, HTTPException
from app.services.partners import get_partners, get_entity_types
from app.models.api.requests import PartnerQuery
from app.models.api.responses import PartnersListResponse, PartnersListData, EntityTypesResponse, EntityTypesData
from app.core.exceptions import PartnerNotFound

router = APIRouter()

@router.get("/",
           response_model=PartnersListResponse,
           summary="Get all partners",
           description="Returns a list of all partners with their entity types")
def read_partners(query: PartnerQuery = Depends()):
    """Get all partners with optional filtering"""
    try:
        partners_data = get_partners()
        
        return PartnersListResponse(
            data=PartnersListData(partners=partners_data),
            message=f"Retrieved {len(partners_data)} partners successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch partners: {str(e)}")

@router.get("/types",
           response_model=EntityTypesResponse,
           summary="Get entity types",
           description="Returns a list of all available entity types")
def read_partner_types():
    """Get all entity types"""
    try:
        entity_types_data = get_entity_types()
        return EntityTypesResponse(
            data=EntityTypesData(entity_types=entity_types_data),
            message="Entity types retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch entity types: {str(e)}")

@router.get("/{partner_id}",
           summary="Get partner by ID",
           description="Returns a specific partner by their ID")
def read_partner(partner_id: str):
    """Get a specific partner by ID"""
    try:
        partners_data = get_partners()
        partner = next((p for p in partners_data if p["id"] == partner_id), None)
        
        if not partner:
            raise PartnerNotFound(partner_id)
        
        return {
            "success": True,
            "partner": partner,
            "message": "Partner retrieved successfully"
        }
    except PartnerNotFound:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch partner: {str(e)}")