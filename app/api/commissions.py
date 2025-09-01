from fastapi import APIRouter, Depends, HTTPException
from app.services.commissions import get_commissions
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
        
        # Apply filtering if needed
        if query.partner_id:
            commissions_data = [c for c in commissions_data if c.partnerId == query.partner_id]
        
        if query.financial_year:
            commissions_data = [c for c in commissions_data if c.financialYear == query.financial_year]
        
        if query.start_date:
            commissions_data = [c for c in commissions_data if c.date >= query.start_date]
        
        if query.end_date:
            commissions_data = [c for c in commissions_data if c.date <= query.end_date]
        
        # Apply pagination
        total = len(commissions_data)
        start = query.offset
        end = start + query.limit
        paginated_commissions = commissions_data[start:end]
        
        return CommissionsListResponse(
            data=CommissionsListData(commissions=paginated_commissions),
            message=f"Retrieved {len(paginated_commissions)} commissions successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch commissions: {str(e)}")

@router.get("/{commission_id}",
           summary="Get commission by ID",
           description="Returns a specific commission by its ID")
def get_commission(commission_id: str):
    """Get a specific commission by ID"""
    try:
        commissions_data = get_commissions()
        commission = next((c for c in commissions_data if c.id == commission_id), None)
        
        if not commission:
            raise CommissionNotFound(commission_id)
        
        return {
            "success": True,
            "commission": commission,
            "message": "Commission retrieved successfully"
        }
    except CommissionNotFound:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch commission: {str(e)}")