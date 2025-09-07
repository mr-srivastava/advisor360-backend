from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ..core.exceptions import (
    DomainException,
    DuplicateError,
    PartnerHasCommissions,
    PartnerNotFound,
)
from ..domain.partner import EntityType
from .dependencies import PartnerServiceDep
from .dtos.common_dtos import SuccessResponse
from .dtos.partner_dtos import (
    CreatePartnerRequest,
    EntityTypesResponse,
    PartnerDetailResponse,
    PartnerListResponse,
    PartnerMapper,
    UpdatePartnerRequest,
)

router = APIRouter()


@router.get(
    "/",
    response_model=PartnerListResponse,
    summary="Get all partners",
    description="Returns a list of all partners with their entity types",
)
async def list_partners(
    partner_service: PartnerServiceDep,
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    search: Optional[str] = Query(None, description="Search by partner name"),
    active_only: bool = Query(True, description="Include only active partners"),
):
    """Get all partners with optional filtering"""
    try:
        if entity_type:
            entity_type_enum = EntityType(entity_type)
            partners = await partner_service.get_partners_by_entity_type(
                entity_type_enum
            )
        elif search:
            partners = await partner_service.search_partners(search)
        elif active_only:
            partners = await partner_service.get_active_partners()
        else:
            partners = await partner_service.get_all_partners()

        # Convert to response DTOs
        partner_responses = PartnerMapper.to_response_list(partners)
        summary = PartnerMapper.create_summary(partners)

        return PartnerListResponse(
            data=partner_responses,
            count=len(partner_responses),
            summary=summary,
            message=f"Retrieved {len(partner_responses)} partners successfully",
        )
    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch partners: {str(e)}"
        )


@router.get(
    "/types",
    response_model=EntityTypesResponse,
    summary="Get entity types",
    description="Returns a list of all available entity types",
)
async def get_entity_types():
    """Get all entity types"""
    try:
        entity_types = PartnerMapper.get_entity_types()

        return EntityTypesResponse(
            data=entity_types,
            count=len(entity_types),
            message="Entity types retrieved successfully",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch entity types: {str(e)}"
        )


@router.get(
    "/{partner_id}",
    response_model=PartnerDetailResponse,
    summary="Get partner by ID",
    description="Returns a specific partner by their ID",
)
async def get_partner(partner_id: str, partner_service: PartnerServiceDep):
    """Get a specific partner by ID"""
    try:
        partner = await partner_service.get_partner_by_id(partner_id)

        # Convert to response DTO
        partner_response = PartnerMapper.to_response(partner)

        return PartnerDetailResponse(
            data=partner_response, message="Partner retrieved successfully"
        )
    except PartnerNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch partner: {str(e)}"
        )


@router.post(
    "/",
    response_model=PartnerDetailResponse,
    summary="Create a new partner",
    description="Creates a new partner record",
)
async def create_partner(
    request: CreatePartnerRequest, partner_service: PartnerServiceDep
):
    """Create a new partner"""
    try:
        entity_type = EntityType(request.entity_type)
        partner = await partner_service.create_partner(
            name=request.name, entity_type=entity_type
        )

        # Convert to response DTO
        partner_response = PartnerMapper.to_response(partner)

        return PartnerDetailResponse(
            data=partner_response, message="Partner created successfully"
        )
    except (DuplicateError, DomainException) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create partner: {str(e)}"
        )


@router.put(
    "/{partner_id}",
    response_model=PartnerDetailResponse,
    summary="Update a partner",
    description="Updates an existing partner record",
)
async def update_partner(
    partner_id: str, request: UpdatePartnerRequest, partner_service: PartnerServiceDep
):
    """Update an existing partner"""
    try:
        entity_type = EntityType(request.entity_type) if request.entity_type else None
        partner = await partner_service.update_partner(
            partner_id=partner_id, name=request.name, entity_type=entity_type
        )

        # Convert to response DTO
        partner_response = PartnerMapper.to_response(partner)

        return PartnerDetailResponse(
            data=partner_response, message="Partner updated successfully"
        )
    except PartnerNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (DuplicateError, DomainException) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update partner: {str(e)}"
        )


@router.delete(
    "/{partner_id}",
    response_model=SuccessResponse,
    summary="Delete a partner",
    description="Deletes an existing partner record",
)
async def delete_partner(partner_id: str, partner_service: PartnerServiceDep):
    """Delete a partner"""
    try:
        success = await partner_service.delete_partner(partner_id)

        if success:
            return SuccessResponse(message="Partner deleted successfully")
        else:
            raise HTTPException(status_code=500, detail="Failed to delete partner")

    except PartnerNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PartnerHasCommissions as e:
        raise HTTPException(status_code=409, detail=str(e))
    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete partner: {str(e)}"
        )
