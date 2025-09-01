from fastapi import APIRouter, Depends, HTTPException
from app.services.commissions import get_commissions, get_commissions_by_fy, get_commissions_by_id
from app.models.api.requests import CommissionQuery
from app.models.api.responses import CommissionsListResponse, CommissionsListData
from app.core.exceptions import CommissionNotFound

router = APIRouter()

@router.get("/",
           response_model=CommissionsListResponse,
           summary="Get all commissions",
           description="Returns a list of all commission transactions with optional filtering")
def list_commissions(query: CommissionQuery = Depends()):
    """Get all commissions with optional filtering and pagination"""
    try:
        commissions_data = get_commissions()
        
        return CommissionsListResponse(
            data=CommissionsListData(commissions=commissions_data),
            message=f"Retrieved {len(commissions_data)} commissions successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch commissions: {str(e)}")

@router.get("/{financial_year}",
           response_model=CommissionsListResponse,
           summary="Get all commissions for a specific financial year",
           description="Returns a list of all commission transactions for a specific financial year")
def list_commissions_by_fy(financial_year: str):
    """Get all commissions for a specific financial year"""
    try:
        commissions_data = get_commissions_by_fy(financial_year)
        return CommissionsListResponse(
            data=CommissionsListData(commissions=commissions_data),
            message=f"Retrieved {len(commissions_data)} commissions successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch commissions: {str(e)}")

@router.get("/{commission_id}",
           summary="Get commission by ID",
           description="Returns a specific commission by its ID")
def get_commission(commission_id: str):
    """Get a specific commission by ID"""
    try:
        commission = get_commissions_by_id(commission_id)
        
        return {
            "success": True,
            "commission": commission,
            "message": "Commission retrieved successfully"
        }
    except CommissionNotFound:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch commission: {str(e)}")