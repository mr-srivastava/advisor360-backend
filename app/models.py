# Legacy models - kept for backward compatibility
# New models should use the structured approach in app/models/

from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

# Users
class User(BaseModel):
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None

# Entity Types
class EntityType(BaseModel):
    name: str

# Entities
class Entity(BaseModel):
    name: str
    type_id: str  # FK to entity_types.id

# Transactions
class EntityTransaction(BaseModel):
    entity_id: str
    month: date
    amount: float