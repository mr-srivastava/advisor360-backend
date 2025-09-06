# Advisor360 Backend Architecture

## Overview

The Advisor360 backend is built using **Clean Architecture** principles with **FastAPI**, implementing a layered approach that separates concerns and promotes maintainability, testability, and scalability.

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                     │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐│
│  │   Commissions   │ │    Partners     │ │   Dashboard     ││
│  │   Endpoints     │ │   Endpoints     │ │   Endpoints     ││
│  └─────────────────┘ └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Service Layer                            │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐│
│  │ CommissionService│ │ PartnerService  │ │DashboardService ││
│  │  (Business Logic)│ │ (Business Logic)│ │(Business Logic) ││
│  └─────────────────┘ └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                  Domain Layer                              │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐│
│  │   Commission    │ │    Partner      │ │  Value Objects  ││
│  │    Entity       │ │    Entity       │ │   (Money, FY)   ││
│  └─────────────────┘ └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                Repository Layer                            │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐│
│  │CommissionRepo   │ │  PartnerRepo    │ │  Supabase       ││
│  │  (Data Access)  │ │  (Data Access)  │ │  Integration    ││
│  └─────────────────┘ └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
app/
├── api/                          # API Layer - FastAPI endpoints
│   ├── dtos/                     # Data Transfer Objects
│   │   ├── commission_dtos.py    # Commission request/response models
│   │   ├── partner_dtos.py       # Partner request/response models
│   │   ├── dashboard_dtos.py     # Dashboard request/response models
│   │   └── common_dtos.py        # Shared DTOs
│   ├── commissions.py            # Commission endpoints
│   ├── partners.py               # Partner endpoints
│   ├── dashboard.py              # Dashboard endpoints
│   └── dependencies.py           # FastAPI dependency injection
│
├── services/                     # Service Layer - Business Logic
│   ├── interfaces/               # Service interfaces
│   │   ├── commission_service.py
│   │   ├── partner_service.py
│   │   └── dashboard_service.py
│   ├── commissions.py            # Commission business logic
│   ├── partners.py               # Partner business logic
│   └── dashboard.py              # Dashboard business logic
│
├── repositories/                 # Repository Layer - Data Access
│   ├── interfaces/               # Repository interfaces
│   │   ├── commission_repository.py
│   │   └── partner_repository.py
│   ├── supabase/                 # Supabase implementations
│   │   ├── commission_repository.py
│   │   └── partner_repository.py
│   └── base_repository.py        # Base repository functionality
│
├── domain/                       # Domain Layer - Business Entities
│   ├── commission.py             # Commission entity
│   ├── partner.py                # Partner entity
│   └── value_objects/            # Value objects
│       ├── money.py              # Money value object
│       └── financial_year.py     # Financial year value object
│
├── core/                         # Core Infrastructure
│   ├── config/                   # Configuration management
│   │   └── app_config.py         # Application configuration
│   ├── exceptions/               # Exception hierarchy
│   │   ├── domain_exceptions.py  # Domain-specific exceptions
│   │   └── infrastructure_exceptions.py
│   ├── middleware/               # Custom middleware
│   │   ├── error_handling_middleware.py
│   │   ├── logging_middleware.py
│   │   └── metrics_middleware.py
│   ├── logging/                  # Logging configuration
│   ├── container.py              # Dependency injection container
│   └── bootstrap.py              # Application bootstrap
│
├── utils/                        # Utility functions
│   └── date_utils.py             # Date/time utilities
│
└── main.py                       # FastAPI application entry point
```

## Key Architectural Patterns

### 1. Dependency Injection

- **Container**: `app/core/container.py` manages all service registrations
- **Bootstrap**: `app/core/bootstrap.py` initializes the DI container
- **FastAPI Integration**: `app/api/dependencies.py` provides FastAPI dependency functions

```python
# Example: Getting a service
from app.core.container import get_container
from app.services.interfaces.commission_service import ICommissionService

container = get_container()
commission_service = container.get(ICommissionService)
```

### 2. Repository Pattern

- **Interfaces**: Define contracts in `app/repositories/interfaces/`
- **Implementations**: Concrete implementations in `app/repositories/supabase/`
- **Abstraction**: Services depend on interfaces, not implementations

### 3. Service Layer

- **Business Logic**: Centralized in service classes
- **Orchestration**: Services coordinate between repositories and domain entities
- **Validation**: Business rule validation happens in services

### 4. Domain-Driven Design

- **Entities**: Rich domain objects with behavior
- **Value Objects**: Immutable objects representing concepts like Money, FinancialYear
- **Domain Services**: Complex business logic that doesn't belong to a single entity

## Adding New Functionality

### 1. Adding a New Entity (e.g., Transaction)

#### Step 1: Create Domain Entity

```python
# app/domain/transaction.py
from dataclasses import dataclass
from datetime import datetime
from .value_objects.money import Money

@dataclass
class Transaction:
    id: str
    commission_id: str
    amount: Money
    transaction_date: datetime
    description: str

    def is_recent(self) -> bool:
        # Domain logic
        pass
```

#### Step 2: Create Repository Interface

```python
# app/repositories/interfaces/transaction_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional
from ...domain.transaction import Transaction

class ITransactionRepository(ABC):
    @abstractmethod
    async def get_by_id(self, transaction_id: str) -> Optional[Transaction]:
        pass

    @abstractmethod
    async def get_by_commission_id(self, commission_id: str) -> List[Transaction]:
        pass
```

#### Step 3: Implement Repository

```python
# app/repositories/supabase/transaction_repository.py
from ..interfaces.transaction_repository import ITransactionRepository
from ...domain.transaction import Transaction

class SupabaseTransactionRepository(ITransactionRepository):
    def __init__(self, supabase_client):
        self.client = supabase_client

    async def get_by_id(self, transaction_id: str) -> Optional[Transaction]:
        # Implementation
        pass
```

#### Step 4: Create Service Interface

```python
# app/services/interfaces/transaction_service.py
from abc import ABC, abstractmethod
from typing import List
from ...domain.transaction import Transaction

class ITransactionService(ABC):
    @abstractmethod
    async def get_transactions_by_commission(self, commission_id: str) -> List[Transaction]:
        pass
```

#### Step 5: Implement Service

```python
# app/services/transactions.py
from .interfaces.transaction_service import ITransactionService
from ..repositories.interfaces.transaction_repository import ITransactionRepository

class TransactionService(ITransactionService):
    def __init__(self, transaction_repo: ITransactionRepository):
        self.transaction_repo = transaction_repo

    async def get_transactions_by_commission(self, commission_id: str) -> List[Transaction]:
        return await self.transaction_repo.get_by_commission_id(commission_id)
```

#### Step 6: Register in DI Container

```python
# app/core/bootstrap.py
def register_dependencies(container: Container) -> None:
    # ... existing registrations

    # Register transaction repository
    container.register(
        ITransactionRepository,
        lambda: SupabaseTransactionRepository(container.get("supabase_client"))
    )

    # Register transaction service
    container.register(
        ITransactionService,
        lambda: TransactionService(container.get(ITransactionRepository))
    )
```

#### Step 7: Create DTOs

```python
# app/api/dtos/transaction_dtos.py
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class TransactionResponse(BaseModel):
    id: str
    commission_id: str
    amount: float
    currency: str
    transaction_date: datetime
    description: str

class TransactionListResponse(BaseModel):
    data: List[TransactionResponse]
    count: int
    message: str
```

#### Step 8: Create API Endpoints

```python
# app/api/transactions.py
from fastapi import APIRouter, Depends
from .dependencies import TransactionServiceDep
from .dtos.transaction_dtos import TransactionListResponse

router = APIRouter()

@router.get("/commission/{commission_id}/transactions", response_model=TransactionListResponse)
async def get_commission_transactions(
    commission_id: str,
    transaction_service: TransactionServiceDep
):
    transactions = await transaction_service.get_transactions_by_commission(commission_id)
    # Map to DTOs and return
```

#### Step 9: Register Router

```python
# app/main.py
from app.api import transactions

app.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
```

### 2. Adding New Business Logic

#### In Services

```python
# app/services/commissions.py
class CommissionService(ICommissionService):
    async def calculate_annual_total(self, partner_id: str, financial_year: str) -> Money:
        commissions = await self.commission_repo.get_by_partner_and_fy(partner_id, financial_year)
        total = sum(commission.amount.value for commission in commissions)
        return Money(total, "INR")
```

#### In Domain Entities

```python
# app/domain/commission.py
@dataclass
class Commission:
    def is_high_value(self) -> bool:
        return self.amount.value > 100000

    def get_financial_quarter(self) -> int:
        # Business logic for determining quarter
        pass
```

### 3. Adding New API Endpoints

#### Follow RESTful conventions:

- `GET /resource` - List resources
- `GET /resource/{id}` - Get specific resource
- `POST /resource` - Create resource
- `PUT /resource/{id}` - Update resource
- `DELETE /resource/{id}` - Delete resource

#### Use proper DTOs:

- Request DTOs for input validation
- Response DTOs for output formatting
- Separate DTOs for different operations (Create, Update, List, Detail)

## Configuration Management

### Environment Variables

```bash
# .env
DATABASE_URL=your_supabase_url
DATABASE_KEY=your_supabase_key
LOG_LEVEL=INFO
ENVIRONMENT=development
```

### Configuration Classes

```python
# app/core/config/app_config.py
class AppConfig(BaseSettings):
    database_url: str
    database_key: str
    log_level: str = "INFO"
    environment: str = "development"
```

## Error Handling

### Exception Hierarchy

```python
# Domain exceptions
DomainException
├── ValidationError
├── NotFoundError
│   ├── PartnerNotFound
│   └── CommissionNotFound
├── BusinessRuleViolation
└── DuplicateError

# Infrastructure exceptions
InfrastructureError
├── DatabaseError
├── ConnectionError
└── TimeoutError
```

### Custom Exception Handling

```python
# app/api/commissions.py
@router.get("/{commission_id}")
async def get_commission(commission_id: str, service: CommissionServiceDep):
    try:
        commission = await service.get_by_id(commission_id)
        return CommissionResponse.from_domain(commission)
    except CommissionNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))
```

## Testing Strategy

### Unit Tests

- Test domain entities and value objects
- Test service business logic
- Mock repository dependencies

### Integration Tests

- Test repository implementations
- Test API endpoints with test database

### Example Test Structure

```python
# tests/services/test_commission_service.py
import pytest
from unittest.mock import Mock
from app.services.commissions import CommissionService

@pytest.fixture
def mock_commission_repo():
    return Mock()

@pytest.fixture
def commission_service(mock_commission_repo):
    return CommissionService(mock_commission_repo)

async def test_get_commission_by_id(commission_service, mock_commission_repo):
    # Test implementation
    pass
```

## Performance Considerations

### Database Optimization

- Use repository pattern for query optimization
- Implement caching at service layer
- Use database indexes appropriately

### API Performance

- Implement pagination for list endpoints
- Use async/await throughout
- Add request/response logging and metrics

### Monitoring

- Structured logging with correlation IDs
- Metrics collection via middleware
- Health check endpoints

## Security Best Practices

### Input Validation

- Use Pydantic models for request validation
- Validate business rules in services
- Sanitize database queries

### Error Handling

- Don't expose internal errors to clients
- Log security-relevant events
- Use proper HTTP status codes

### Configuration

- Store secrets in environment variables
- Use different configurations per environment
- Validate configuration on startup

## Deployment Considerations

### Environment Setup

- Use environment-specific configuration
- Implement proper logging levels
- Set up health checks

### Database Migrations

- Version control database schema changes
- Use migration scripts for schema updates
- Test migrations in staging environment

### Monitoring

- Set up application metrics
- Monitor database performance
- Implement alerting for critical errors

This architecture provides a solid foundation for building scalable, maintainable applications while following clean architecture principles and best practices.
