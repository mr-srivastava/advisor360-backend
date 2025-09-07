# Repository interfaces

from .commission_repository import ICommissionRepository
from .partner_repository import IPartnerRepository
from .transaction_repository import ITransactionRepository

__all__ = ["ICommissionRepository", "IPartnerRepository", "ITransactionRepository"]
