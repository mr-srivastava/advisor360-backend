"""Partner service implementation providing business logic for partner operations."""

from typing import Optional

from ..core.exceptions import (
    DuplicateError,
    ExternalServiceError,
    PartnerHasCommissions,
    PartnerNotFound,
    ValidationError,
)
from ..domain.partner import EntityType, Partner
from ..repositories.interfaces.commission_repository import ICommissionRepository
from ..repositories.interfaces.partner_repository import IPartnerRepository
from .interfaces.partner_service import IPartnerService


class PartnerService(IPartnerService):
    """Partner service implementation providing business logic for partner operations.

    Coordinates between partner and commission repositories to provide high-level
    business functionality for partner management.
    """

    def __init__(
        self,
        partner_repository: IPartnerRepository,
        commission_repository: ICommissionRepository,
    ):
        self._partner_repo = partner_repository
        self._commission_repo = commission_repository

    async def get_all_partners(self) -> list[Partner]:
        """Retrieve all partners in the system."""
        try:
            result: list[Partner] = await self._partner_repo.get_all()
            return result
        except Exception as e:
            raise ExternalServiceError(f"Failed to retrieve partners: {str(e)}") from e

    async def get_partner_by_id(self, partner_id: str) -> Partner:
        """Retrieve a specific partner by ID."""
        try:
            partner = await self._partner_repo.get_by_id(partner_id)
            if not partner:
                raise PartnerNotFound(partner_id)
            return partner
        except PartnerNotFound:
            raise
        except Exception as e:
            raise ExternalServiceError(f"Failed to retrieve partner: {str(e)}") from e

    async def get_partner_by_name(self, name: str) -> Optional[Partner]:
        """Retrieve a partner by exact name."""
        try:
            return await self._partner_repo.get_by_name(name)
        except Exception as e:
            raise ExternalServiceError(
                f"Failed to retrieve partner by name: {str(e)}"
            ) from e

    async def get_partners_by_entity_type(
        self, entity_type: EntityType
    ) -> list[Partner]:
        """Retrieve all partners of a specific entity type."""
        try:
            result: list[Partner] = await self._partner_repo.get_by_entity_type(
                entity_type
            )
            return result
        except Exception as e:
            raise ExternalServiceError(
                f"Failed to retrieve partners by entity type: {str(e)}"
            ) from e

    async def create_partner(self, name: str, entity_type: EntityType) -> Partner:
        """Create a new partner."""
        try:
            # Validate name uniqueness
            existing_partner = await self._partner_repo.get_by_name(name.strip())
            if existing_partner:
                raise DuplicateError(f"Partner with name '{name}' already exists")

            # Create domain object
            import uuid

            partner_id = str(uuid.uuid4())
            partner = Partner(id=partner_id, name=name.strip(), entity_type=entity_type)

            # Save to repository
            return await self._partner_repo.create(partner)
        except (ValidationError, DuplicateError):
            raise
        except Exception as e:
            raise ExternalServiceError(f"Failed to create partner: {str(e)}") from e

    async def update_partner(
        self,
        partner_id: str,
        name: Optional[str] = None,
        entity_type: Optional[EntityType] = None,
    ) -> Partner:
        """Update an existing partner."""
        try:
            # Get existing partner
            partner = await self._partner_repo.get_by_id(partner_id)
            if not partner:
                raise PartnerNotFound(partner_id)

            # Check name uniqueness if updating name
            if name and name.strip() != partner.name:
                existing_partner = await self._partner_repo.get_by_name(name.strip())
                if existing_partner and existing_partner.id != partner_id:
                    raise DuplicateError(f"Partner with name '{name}' already exists")

            # Apply updates
            updated_partner = partner
            if name is not None:
                updated_partner = updated_partner.update_name(name.strip())

            if entity_type is not None:
                updated_partner = updated_partner.update_entity_type(entity_type)

            # Save changes
            return await self._partner_repo.update(partner_id, updated_partner)
        except (PartnerNotFound, ValidationError, DuplicateError):
            raise
        except Exception as e:
            raise ExternalServiceError(f"Failed to update partner: {str(e)}") from e

    async def delete_partner(self, partner_id: str) -> bool:
        """Delete a partner."""
        try:
            # Verify partner exists
            partner = await self._partner_repo.get_by_id(partner_id)
            if not partner:
                raise PartnerNotFound(partner_id)

            # Check if partner has commissions
            commissions = await self._commission_repo.get_by_partner_id(partner_id)
            if commissions:
                raise PartnerHasCommissions(
                    f"Cannot delete partner with {len(commissions)} associated commissions"
                )

            result: bool = await self._partner_repo.delete(partner_id)
            return result
        except (PartnerNotFound, PartnerHasCommissions):
            raise
        except Exception as e:
            raise ExternalServiceError(f"Failed to delete partner: {str(e)}") from e

    async def search_partners(self, search_term: str) -> list[Partner]:
        """Search partners by name."""
        try:
            result: list[Partner] = await self._partner_repo.search_by_name(search_term)
            return result
        except Exception as e:
            raise ExternalServiceError(f"Failed to search partners: {str(e)}") from e

    async def get_active_partners(self) -> list[Partner]:
        """Retrieve all active partners."""
        try:
            result: list[Partner] = await self._partner_repo.get_active_partners()
            return result
        except Exception as e:
            raise ExternalServiceError(
                f"Failed to retrieve active partners: {str(e)}"
            ) from e

    async def get_partners_with_commissions(self) -> list[Partner]:
        """Retrieve partners who have at least one commission."""
        try:
            result: list[Partner] = (
                await self._partner_repo.get_partners_with_commissions()
            )
            return result
        except Exception as e:
            raise ExternalServiceError(
                f"Failed to retrieve partners with commissions: {str(e)}"
            ) from e

    async def get_partners_without_commissions(self) -> list[Partner]:
        """Retrieve partners who have no commissions."""
        try:
            result: list[Partner] = (
                await self._partner_repo.get_partners_without_commissions()
            )
            return result
        except Exception as e:
            raise ExternalServiceError(
                f"Failed to retrieve partners without commissions: {str(e)}"
            ) from e

    async def get_entity_type_statistics(self) -> dict[str, int]:
        """Get count of partners by entity type."""
        try:
            entity_type_counts = await self._partner_repo.get_entity_type_counts()
            # Convert enum keys to string values
            return {
                entity_type.value: count
                for entity_type, count in entity_type_counts.items()
            }
        except Exception as e:
            raise ExternalServiceError(
                f"Failed to calculate entity type statistics: {str(e)}"
            ) from e

    async def validate_partner_name(
        self, name: str, exclude_id: Optional[str] = None
    ) -> bool:
        """Validate if a partner name is available."""
        try:
            return not await self._partner_repo.name_exists(name.strip(), exclude_id)
        except Exception as e:
            raise ExternalServiceError(
                f"Failed to validate partner name: {str(e)}"
            ) from e

    async def get_recently_created_partners(self, limit: int = 10) -> list[Partner]:
        """Get the most recently created partners."""
        try:
            result: list[Partner] = await self._partner_repo.get_recently_created(limit)
            return result
        except Exception as e:
            raise ExternalServiceError(
                f"Failed to retrieve recent partners: {str(e)}"
            ) from e
