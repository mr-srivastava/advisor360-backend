"""Database entity models for Advisor360 application"""

from datetime import datetime
from typing import Optional

from pydantic import Field

from app.models.base import BaseEntity


class EntityTypeDB(BaseEntity):
    """Database model for entity types"""

    name: str = Field(..., min_length=1, max_length=100, description="Entity type name")


class EntityDB(BaseEntity):
    """Database model for entities/partners"""

    name: str = Field(..., min_length=1, max_length=255, description="Entity name")
    type_id: str = Field(..., description="Foreign key to entity_types table")

    class Config:
        from_attributes = True


class EntityTransactionDB(BaseEntity):
    """Database model for entity transactions/commissions"""

    entity_id: str = Field(..., description="Foreign key to entities table")
    month: datetime = Field(..., description="Transaction month")
    amount: float = Field(..., ge=0, description="Transaction amount")
    description: Optional[str] = Field(
        None, max_length=500, description="Transaction description"
    )

    class Config:
        from_attributes = True


class UserDB(BaseEntity):
    """Database model for users"""

    email: str = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, max_length=255, description="User full name")
    avatar_url: Optional[str] = Field(None, description="User avatar URL")

    class Config:
        from_attributes = True
