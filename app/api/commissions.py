from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ..core.exceptions import CommissionNotFound, DomainException, PartnerNotFound
from .dependencies import CommissionServiceDep, PartnerServiceDep
from .dtos.commission_dtos import (
    CommissionDetailResponse,
    CommissionListResponse,
    CommissionMapper,
    CommissionMatrixResponse,
    CreateCommissionRequest,
    UpdateCommissionRequest,
)
from .dtos.common_dtos import SuccessResponse

router = APIRouter()


@router.get(
    "/",
    response_model=CommissionListResponse,
    summary="Get all commissions",
    description="Returns a list of all commission transactions with optional filtering",
)
async def list_commissions(
    commission_service: CommissionServiceDep,
    partner_service: PartnerServiceDep,
    partner_id: Optional[str] = Query(None, description="Filter by partner ID"),
    financial_year: Optional[str] = Query(
        None, description="Filter by financial year (e.g., FY24-25)"
    ),
):
    """Get all commissions with optional filtering"""
    try:
        if partner_id:
            commissions = await commission_service.get_commissions_by_partner(
                partner_id
            )
        elif financial_year:
            commissions = await commission_service.get_commissions_by_financial_year(
                financial_year
            )
        else:
            # Get all commissions ordered by creation date (newest first)
            commissions = await commission_service.get_all_commissions_ordered()

        # Get partners for enriching response
        partners = await partner_service.get_all_partners()

        # Convert to response DTOs
        commission_responses = CommissionMapper.to_response_list(commissions, partners)
        summary = CommissionMapper.create_summary(commissions, financial_year)

        return CommissionListResponse(
            data=commission_responses,
            count=len(commission_responses),
            summary=summary,
            message=f"Retrieved {len(commission_responses)} commissions successfully",
        )
    except (PartnerNotFound, DomainException) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch commissions: {str(e)}"
        )


@router.get(
    "/{commission_id}",
    response_model=CommissionDetailResponse,
    summary="Get commission by ID",
    description="Returns a specific commission by its ID",
)
async def get_commission(
    commission_id: str,
    commission_service: CommissionServiceDep,
    partner_service: PartnerServiceDep,
):
    """Get a specific commission by ID"""
    try:
        commission = await commission_service.get_commission_by_id(commission_id)

        # Get partner information
        partner = await partner_service.get_partner_by_id(commission.partner_id)

        # Convert to response DTO
        commission_response = CommissionMapper.to_response(commission, partner)

        return CommissionDetailResponse(
            data=commission_response, message="Commission retrieved successfully"
        )
    except CommissionNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (PartnerNotFound, DomainException) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch commission: {str(e)}"
        )


@router.post(
    "/",
    response_model=CommissionDetailResponse,
    summary="Create a new commission",
    description="Creates a new commission record",
)
async def create_commission(
    request: CreateCommissionRequest,
    commission_service: CommissionServiceDep,
    partner_service: PartnerServiceDep,
):
    """Create a new commission"""
    try:
        commission = await commission_service.create_commission(
            partner_id=request.partner_id,
            amount=request.amount,
            transaction_date=request.transaction_date,
            description=request.description,
        )

        # Get partner information
        partner = await partner_service.get_partner_by_id(commission.partner_id)

        # Convert to response DTO
        commission_response = CommissionMapper.to_response(commission, partner)

        return CommissionDetailResponse(
            data=commission_response, message="Commission created successfully"
        )
    except (PartnerNotFound, DomainException) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create commission: {str(e)}"
        )


@router.put(
    "/{commission_id}",
    response_model=CommissionDetailResponse,
    summary="Update a commission",
    description="Updates an existing commission record",
)
async def update_commission(
    commission_id: str,
    request: UpdateCommissionRequest,
    commission_service: CommissionServiceDep,
    partner_service: PartnerServiceDep,
):
    """Update an existing commission"""
    try:
        commission = await commission_service.update_commission(
            commission_id=commission_id,
            amount=request.amount,
            description=request.description,
        )

        # Get partner information
        partner = await partner_service.get_partner_by_id(commission.partner_id)

        # Convert to response DTO
        commission_response = CommissionMapper.to_response(commission, partner)

        return CommissionDetailResponse(
            data=commission_response, message="Commission updated successfully"
        )
    except CommissionNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (PartnerNotFound, DomainException) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update commission: {str(e)}"
        )


@router.delete(
    "/{commission_id}",
    response_model=SuccessResponse,
    summary="Delete a commission",
    description="Deletes an existing commission record",
)
async def delete_commission(
    commission_id: str, commission_service: CommissionServiceDep
):
    """Delete a commission"""
    try:
        success = await commission_service.delete_commission(commission_id)

        if success:
            return SuccessResponse(message="Commission deleted successfully")
        else:
            raise HTTPException(status_code=500, detail="Failed to delete commission")

    except CommissionNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete commission: {str(e)}"
        )


@router.get(
    "/matrix/{financial_year}",
    response_model=CommissionMatrixResponse,
    summary="Get Matrix View for Commission by FY",
)
async def get_commission_matrix_by_fy(
    financial_year: str,
    commission_service: CommissionServiceDep,
):
    """Get Matrix View for Commission by FY"""
    try:
        get_commission_matrix_by_fy = (
            await commission_service.get_commission_matrix_by_fy(financial_year)
        )
        return CommissionMapper.to_matrix_response(get_commission_matrix_by_fy)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get commission matrix: {str(e)}"
        )
