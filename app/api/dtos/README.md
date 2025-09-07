# API DTOs (Data Transfer Objects)

This directory contains all the Data Transfer Objects (DTOs) used for API communication in the application. DTOs provide a clean separation between the domain models and the API layer, ensuring that internal data structures are decoupled from external API contracts.

## Structure

```
app/api/dtos/
├── __init__.py              # Main exports
├── common_dtos.py           # Common/shared DTOs
├── commission_dtos.py       # Commission-specific DTOs
├── partner_dtos.py          # Partner-specific DTOs
├── transaction_dtos.py      # Transaction-specific DTOs
├── dashboard_dtos.py        # Dashboard-specific DTOs
├── mappers.py              # Centralized mapping utilities
├── usage_examples.py       # Usage examples and documentation
└── README.md               # This file
```

## Key Concepts

### 1. Request DTOs

Used for validating and parsing incoming API requests:

- `CreateCommissionRequest`
- `UpdateCommissionRequest`
- `CreatePartnerRequest`
- `UpdatePartnerRequest`
- `CreateTransactionRequest`
- `UpdateTransactionRequest`

### 2. Response DTOs

Used for formatting outgoing API responses:

- `CommissionResponse`
- `PartnerResponse`
- `TransactionResponse`
- Various list and paginated response types

### 3. Query Parameter DTOs

Used for validating query parameters:

- `CommissionQueryParams`
- `PartnerQueryParams`
- `TransactionQueryParams`
- `DashboardQueryParams`

### 4. Common DTOs

Shared across all endpoints:

- `BaseResponse`
- `ErrorResponse`
- `PaginatedResponse`
- `DataResponse`
- `ListResponse`

## Usage Examples

### Creating a Commission

```python
from app.api.dtos import CreateCommissionRequest, CommissionResponse

# Parse request data
request_data = {
    "partner_id": "partner-123",
    "amount": 1500.0,
    "transaction_date": "2024-06-15",
    "description": "Monthly commission"
}

# Validate and create request DTO
create_request = CreateCommissionRequest(**request_data)

# Convert to domain model
commission = create_request.to_domain()

# After processing, convert to response
response = CommissionResponse.from_domain(commission, partner)
```

### Using Mappers

```python
from app.api.dtos import DomainToDTOMapper

# Convert single commission
commission_response = DomainToDTOMapper.commission_to_response(commission, partner)

# Convert list of commissions
commission_list = DomainToDTOMapper.commissions_to_response_list(commissions, partners)

# Create summary
summary = DomainToDTOMapper.create_commission_summary(commissions)
```

### Error Handling

```python
from app.api.dtos import ErrorResponse, ErrorDetail

try:
    # Some operation
    pass
except ValidationError as e:
    return ErrorResponse(
        message="Validation failed",
        details=[
            ErrorDetail(
                field="amount",
                message="Amount must be positive",
                code="INVALID_VALUE"
            )
        ]
    )
```

### Pagination

```python
from app.api.dtos import PaginatedResponse, PaginationMeta

# Create pagination metadata
pagination_meta = PaginationMeta(
    page=1,
    per_page=10,
    total=100,
    pages=10,
    has_next=True,
    has_prev=False
)

# Create paginated response
return PaginatedResponse[CommissionResponse](
    data=commission_responses,
    meta=pagination_meta,
    message="Commissions retrieved successfully"
)
```

## Validation

All DTOs include comprehensive validation using Pydantic:

### Built-in Validations

- Type checking
- Required field validation
- String length constraints
- Numeric range constraints
- Date validation

### Custom Validations

- Business rule validation
- Cross-field validation
- Format validation (e.g., financial year format)
- Domain-specific constraints

### Example Custom Validator

```python
from pydantic import validator

class CreateCommissionRequest(BaseModel):
    amount: float = Field(..., gt=0)
    transaction_date: date

    @validator('transaction_date')
    def validate_transaction_date(cls, v):
        if v > date.today():
            raise ValueError('Transaction date cannot be in the future')
        return v
```

## Mapping Between Layers

The DTOs provide clean mapping between different layers:

```
API Layer (DTOs) ←→ Service Layer ←→ Domain Layer (Models)
```

### Domain to DTO Mapping

```python
# Commission domain model to response DTO
commission_response = CommissionResponse.from_domain(commission, partner)

# Using centralized mapper
commission_response = DomainToDTOMapper.commission_to_response(commission, partner)
```

### DTO to Domain Mapping

```python
# Request DTO to domain model
commission = create_request.to_domain()

# With additional processing
commission = Commission.create_new(
    partner_id=create_request.partner_id,
    amount=Money.from_float(create_request.amount, create_request.currency),
    transaction_date=create_request.transaction_date,
    description=create_request.description
)
```

## Response Formats

### Standard Success Response

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "timestamp": "2024-06-15T10:30:00Z"
}
```

### Data Response

```json
{
  "success": true,
  "message": "Commission retrieved successfully",
  "timestamp": "2024-06-15T10:30:00Z",
  "data": {
    "id": "comm-123",
    "partner_id": "partner-123",
    "amount": 1500.0,
    "currency": "INR"
    // ... other fields
  }
}
```

### List Response

```json
{
  "success": true,
  "message": "Commissions retrieved successfully",
  "timestamp": "2024-06-15T10:30:00Z",
  "data": [
    {
      "id": "comm-123"
      // ... commission data
    }
  ],
  "count": 1,
  "summary": {
    "total_amount": 1500.0,
    "currency": "INR",
    "count": 1,
    "average_amount": 1500.0,
    "financial_year": "FY24-25"
  }
}
```

### Paginated Response

```json
{
  "success": true,
  "message": "Page 1 of 10 retrieved successfully",
  "timestamp": "2024-06-15T10:30:00Z",
  "data": [
    // ... items
  ],
  "meta": {
    "page": 1,
    "per_page": 10,
    "total": 100,
    "pages": 10,
    "has_next": true,
    "has_prev": false
  }
}
```

### Error Response

```json
{
  "success": false,
  "message": "Validation failed",
  "timestamp": "2024-06-15T10:30:00Z",
  "details": [
    {
      "field": "amount",
      "message": "Amount must be positive",
      "code": "INVALID_VALUE"
    }
  ],
  "request_id": "req-123"
}
```

## Best Practices

### 1. Always Use DTOs for API Boundaries

Never expose domain models directly through APIs. Always use DTOs to maintain clean separation.

### 2. Validate Early

Use Pydantic validators to catch validation errors as early as possible in the request processing pipeline.

### 3. Use Centralized Mappers

Use the centralized mapping utilities in `mappers.py` to ensure consistency and reduce code duplication.

### 4. Include Comprehensive Documentation

All DTO fields should include clear descriptions using Pydantic's `Field` with description parameters.

### 5. Handle Errors Gracefully

Always return standardized error responses using the `ErrorResponse` DTO.

### 6. Use Type Hints

Always use proper type hints for better IDE support and runtime validation.

### 7. Keep DTOs Simple

DTOs should be simple data containers. Complex business logic should remain in the domain layer.

## Testing DTOs

```python
def test_commission_dto_validation():
    # Test valid data
    valid_data = {
        "partner_id": "partner-123",
        "amount": 1500.0,
        "transaction_date": "2024-06-15"
    }
    request = CreateCommissionRequest(**valid_data)
    assert request.partner_id == "partner-123"

    # Test invalid data
    invalid_data = {
        "partner_id": "",
        "amount": -100.0,
        "transaction_date": "2025-12-31"
    }

    with pytest.raises(ValidationError):
        CreateCommissionRequest(**invalid_data)
```

## Integration with FastAPI

```python
from fastapi import APIRouter, HTTPException
from app.api.dtos import CreateCommissionRequest, CommissionResponse

router = APIRouter()

@router.post("/commissions", response_model=CommissionResponse)
async def create_commission(request: CreateCommissionRequest):
    try:
        # Convert to domain model
        commission = request.to_domain()

        # Process through service layer
        created_commission = await commission_service.create(commission)

        # Convert to response DTO
        return CommissionResponse.from_domain(created_commission)

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

This DTO system provides a robust, type-safe, and maintainable way to handle API communication while keeping the domain models clean and focused on business logic.
