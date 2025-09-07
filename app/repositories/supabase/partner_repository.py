"""Supabase implementation of the Partner repository."""

import logging
from typing import Optional

from postgrest.exceptions import APIError
from supabase import Client

from ...core.exceptions.repository_exceptions import RepositoryError
from ...domain.partner import EntityType, Partner
from ..interfaces.partner_repository import IPartnerRepository
from ..models.partner_model import PartnerModel
from .base_repository import BaseSupabaseRepository

logger = logging.getLogger(__name__)


class PartnerRepository(
    BaseSupabaseRepository[Partner, PartnerModel], IPartnerRepository
):
    """Supabase implementation of the Partner repository.

    Provides partner-specific data access operations using Supabase as the backend.
    Maps between Partner domain models and the entities table with entity_types join.
    """

    def __init__(self, supabase_client: Client):
        """Initialize the Partner repository.

        Args:
            supabase_client: Supabase client instance
        """
        super().__init__(supabase_client, "entities", PartnerModel)
        self._logger = logging.getLogger(f"{__name__}.PartnerRepository")

    async def get_by_name(self, name: str) -> Optional[Partner]:
        """Retrieve a partner by their exact name.

        Args:
            name: The exact name of the partner

        Returns:
            The partner if found, None otherwise

        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        try:
            if not name or not name.strip():
                raise ValueError("Partner name cannot be empty")

            name = name.strip()
            self._logger.debug(f"Fetching partner by name: {name}")

            response = (
                self._client.table(self._table_name)
                .select("*, entity_types(name)")
                .eq("name", name)
                .execute()
            )

            if not response.data:
                self._logger.debug(f"No partner found with name: {name}")
                return None

            # Flatten the joined data
            row = response.data[0]
            if row.get("entity_types"):
                row["entity_type_name"] = row["entity_types"]["name"]

            db_model = PartnerModel.from_database_row(row)
            partner = db_model.to_domain()

            self._logger.debug(f"Successfully retrieved partner by name: {name}")
            return partner

        except APIError as e:
            self._logger.error(
                f"Supabase API error retrieving partner by name {name}: {e}"
            )
            raise RepositoryError(
                f"Failed to retrieve partner by name: {str(e)}"
            ) from e
        except Exception as e:
            self._logger.error(
                f"Unexpected error retrieving partner by name {name}: {e}"
            )
            raise RepositoryError(
                f"Unexpected error retrieving partner by name: {str(e)}"
            ) from e

    async def get_by_entity_type(self, entity_type: EntityType) -> list[Partner]:
        """Retrieve all partners of a specific entity type.

        Args:
            entity_type: The entity type to filter by

        Returns:
            List of partners with the specified entity type

        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        try:
            type_id = PartnerModel._map_entity_type_enum_to_id(entity_type)

            self._logger.debug(f"Fetching partners by entity type: {entity_type}")

            response = (
                self._client.table(self._table_name)
                .select("*, entity_types(name)")
                .eq("type_id", type_id)
                .order("name")
                .execute()
            )

            partners = []
            for row in response.data:
                # Flatten the joined data
                if row.get("entity_types"):
                    row["entity_type_name"] = row["entity_types"]["name"]

                db_model = PartnerModel.from_database_row(row)
                partner = db_model.to_domain()
                partners.append(partner)

            self._logger.debug(
                f"Retrieved {len(partners)} partners for entity type {entity_type}"
            )
            return partners

        except APIError as e:
            self._logger.error(
                f"Supabase API error retrieving partners by entity type {entity_type}: {e}"
            )
            raise RepositoryError(
                f"Failed to retrieve partners by entity type: {str(e)}"
            ) from e
        except Exception as e:
            self._logger.error(
                f"Unexpected error retrieving partners by entity type {entity_type}: {e}"
            )
            raise RepositoryError(
                f"Unexpected error retrieving partners by entity type: {str(e)}"
            ) from e

    async def search_by_name(self, search_term: str) -> list[Partner]:
        """Search partners by name using partial matching.

        Args:
            search_term: The text to search for in partner names

        Returns:
            List of partners with names containing the search term

        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        try:
            if not search_term or not search_term.strip():
                raise ValueError("Search term cannot be empty")

            search_term = search_term.strip()
            self._logger.debug(f"Searching partners by name: {search_term}")

            response = (
                self._client.table(self._table_name)
                .select("*, entity_types(name)")
                .ilike("name", f"%{search_term}%")
                .order("name")
                .execute()
            )

            partners = []
            for row in response.data:
                # Flatten the joined data
                if row.get("entity_types"):
                    row["entity_type_name"] = row["entity_types"]["name"]

                db_model = PartnerModel.from_database_row(row)
                partner = db_model.to_domain()
                partners.append(partner)

            self._logger.debug(f"Found {len(partners)} partners matching name search")
            return partners

        except APIError as e:
            self._logger.error(f"Supabase API error searching partners by name: {e}")
            raise RepositoryError(f"Failed to search partners by name: {str(e)}") from e
        except ValueError:
            raise
        except Exception as e:
            self._logger.error(f"Unexpected error searching partners by name: {e}")
            raise RepositoryError(
                f"Unexpected error searching partners by name: {str(e)}"
            ) from e

    async def get_active_partners(self) -> list[Partner]:
        """Retrieve all active partners.

        Returns:
            List of active partners

        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        try:
            self._logger.debug("Fetching all active partners")

            # For now, all partners are considered active
            # This can be extended with an 'active' column in the future
            response = (
                self._client.table(self._table_name)
                .select("*, entity_types(name)")
                .order("name")
                .execute()
            )

            partners = []
            for row in response.data:
                # Flatten the joined data
                if row.get("entity_types"):
                    row["entity_type_name"] = row["entity_types"]["name"]

                db_model = PartnerModel.from_database_row(row)
                partner = db_model.to_domain()
                if partner.is_active():  # Domain logic for active status
                    partners.append(partner)

            self._logger.debug(f"Retrieved {len(partners)} active partners")
            return partners

        except APIError as e:
            self._logger.error(f"Supabase API error retrieving active partners: {e}")
            raise RepositoryError(
                f"Failed to retrieve active partners: {str(e)}"
            ) from e
        except Exception as e:
            self._logger.error(f"Unexpected error retrieving active partners: {e}")
            raise RepositoryError(
                f"Unexpected error retrieving active partners: {str(e)}"
            ) from e

    async def get_partners_with_commissions(self) -> list[Partner]:
        """Retrieve partners who have at least one commission.

        Returns:
            List of partners with commissions

        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        try:
            self._logger.debug("Fetching partners with commissions")

            # Use a subquery to find partners with commissions
            response = (
                self._client.table(self._table_name)
                .select("*, entity_types(name)")
                .in_(
                    "id",
                    self._client.table("entity_transactions")
                    .select("entity_id")
                    .execute()
                    .data,
                )
                .order("name")
                .execute()
            )

            partners = []
            for row in response.data:
                # Flatten the joined data
                if row.get("entity_types"):
                    row["entity_type_name"] = row["entity_types"]["name"]

                db_model = PartnerModel.from_database_row(row)
                partner = db_model.to_domain()
                partners.append(partner)

            self._logger.debug(f"Retrieved {len(partners)} partners with commissions")
            return partners

        except APIError as e:
            self._logger.error(
                f"Supabase API error retrieving partners with commissions: {e}"
            )
            raise RepositoryError(
                f"Failed to retrieve partners with commissions: {str(e)}"
            ) from e
        except Exception as e:
            self._logger.error(
                f"Unexpected error retrieving partners with commissions: {e}"
            )
            raise RepositoryError(
                f"Unexpected error retrieving partners with commissions: {str(e)}"
            ) from e

    async def get_partners_without_commissions(self) -> list[Partner]:
        """Retrieve partners who have no commissions.

        Returns:
            List of partners without commissions

        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        try:
            self._logger.debug("Fetching partners without commissions")

            # Get all partner IDs that have commissions
            commission_response = (
                self._client.table("entity_transactions").select("entity_id").execute()
            )

            partner_ids_with_commissions = {
                row["entity_id"] for row in commission_response.data
            }

            # Get all partners
            all_partners_response = (
                self._client.table(self._table_name)
                .select("*, entity_types(name)")
                .order("name")
                .execute()
            )

            partners = []
            for row in all_partners_response.data:
                if row["id"] not in partner_ids_with_commissions:
                    # Flatten the joined data
                    if row.get("entity_types"):
                        row["entity_type_name"] = row["entity_types"]["name"]

                    db_model = PartnerModel.from_database_row(row)
                    partner = db_model.to_domain()
                    partners.append(partner)

            self._logger.debug(
                f"Retrieved {len(partners)} partners without commissions"
            )
            return partners

        except APIError as e:
            self._logger.error(
                f"Supabase API error retrieving partners without commissions: {e}"
            )
            raise RepositoryError(
                f"Failed to retrieve partners without commissions: {str(e)}"
            ) from e
        except Exception as e:
            self._logger.error(
                f"Unexpected error retrieving partners without commissions: {e}"
            )
            raise RepositoryError(
                f"Unexpected error retrieving partners without commissions: {str(e)}"
            ) from e

    async def get_entity_type_counts(self) -> dict[EntityType, int]:
        """Get count of partners by entity type.

        Returns:
            Dictionary mapping entity types to partner counts

        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        try:
            self._logger.debug("Calculating entity type counts")

            response = (
                self._client.table(self._table_name)
                .select("type_id, entity_types(name)")
                .execute()
            )

            type_counts = {}
            for row in response.data:
                entity_type_name = row.get("entity_types", {}).get("name", "Unknown")
                entity_type = PartnerModel._map_entity_type_name_to_enum(
                    entity_type_name
                )

                if entity_type not in type_counts:
                    type_counts[entity_type] = 0
                type_counts[entity_type] += 1

            self._logger.debug(f"Entity type counts: {type_counts}")
            return type_counts

        except APIError as e:
            self._logger.error(
                f"Supabase API error calculating entity type counts: {e}"
            )
            raise RepositoryError(
                f"Failed to calculate entity type counts: {str(e)}"
            ) from e
        except Exception as e:
            self._logger.error(f"Unexpected error calculating entity type counts: {e}")
            raise RepositoryError(
                f"Unexpected error calculating entity type counts: {str(e)}"
            ) from e

    async def name_exists(self, name: str, exclude_id: Optional[str] = None) -> bool:
        """Check if a partner name already exists.

        Args:
            name: The name to check
            exclude_id: Optional partner ID to exclude from the check (for updates)

        Returns:
            True if the name exists, False otherwise

        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        try:
            if not name or not name.strip():
                raise ValueError("Partner name cannot be empty")

            name = name.strip()
            self._logger.debug(f"Checking if partner name exists: {name}")

            query = self._client.table(self._table_name).select("id").eq("name", name)

            if exclude_id:
                query = query.neq("id", exclude_id)

            response = query.execute()

            exists = len(response.data) > 0
            self._logger.debug(f"Partner name '{name}' exists: {exists}")
            return exists

        except APIError as e:
            self._logger.error(f"Supabase API error checking name existence: {e}")
            raise RepositoryError(f"Failed to check name existence: {str(e)}") from e
        except ValueError:
            raise
        except Exception as e:
            self._logger.error(f"Unexpected error checking name existence: {e}")
            raise RepositoryError(
                f"Unexpected error checking name existence: {str(e)}"
            ) from e

    async def get_recently_created(self, limit: int = 10) -> list[Partner]:
        """Retrieve the most recently created partners.

        Args:
            limit: Maximum number of partners to return

        Returns:
            List of recent partners ordered by creation date (newest first)

        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        try:
            if limit <= 0:
                raise ValueError("Limit must be positive")

            self._logger.debug(f"Fetching {limit} recently created partners")

            response = (
                self._client.table(self._table_name)
                .select("*, entity_types(name)")
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            partners = []
            for row in response.data:
                # Flatten the joined data
                if row.get("entity_types"):
                    row["entity_type_name"] = row["entity_types"]["name"]

                db_model = PartnerModel.from_database_row(row)
                partner = db_model.to_domain()
                partners.append(partner)

            self._logger.debug(f"Retrieved {len(partners)} recently created partners")
            return partners

        except APIError as e:
            self._logger.error(
                f"Supabase API error retrieving recently created partners: {e}"
            )
            raise RepositoryError(
                f"Failed to retrieve recently created partners: {str(e)}"
            ) from e
        except ValueError:
            raise
        except Exception as e:
            self._logger.error(
                f"Unexpected error retrieving recently created partners: {e}"
            )
            raise RepositoryError(
                f"Unexpected error retrieving recently created partners: {str(e)}"
            ) from e

    async def get_recently_updated(self, limit: int = 10) -> list[Partner]:
        """Retrieve the most recently updated partners.

        Args:
            limit: Maximum number of partners to return

        Returns:
            List of recently updated partners ordered by update date (newest first)

        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        try:
            if limit <= 0:
                raise ValueError("Limit must be positive")

            self._logger.debug(f"Fetching {limit} recently updated partners")

            response = (
                self._client.table(self._table_name)
                .select("*, entity_types(name)")
                .not_.is_("updated_at", "null")
                .order("updated_at", desc=True)
                .limit(limit)
                .execute()
            )

            partners = []
            for row in response.data:
                # Flatten the joined data
                if row.get("entity_types"):
                    row["entity_type_name"] = row["entity_types"]["name"]

                db_model = PartnerModel.from_database_row(row)
                partner = db_model.to_domain()
                partners.append(partner)

            self._logger.debug(f"Retrieved {len(partners)} recently updated partners")
            return partners

        except APIError as e:
            self._logger.error(
                f"Supabase API error retrieving recently updated partners: {e}"
            )
            raise RepositoryError(
                f"Failed to retrieve recently updated partners: {str(e)}"
            ) from e
        except ValueError:
            raise
        except Exception as e:
            self._logger.error(
                f"Unexpected error retrieving recently updated partners: {e}"
            )
            raise RepositoryError(
                f"Unexpected error retrieving recently updated partners: {str(e)}"
            ) from e

    async def get_all(self, filters: Optional[dict[str, any]] = None) -> list[Partner]:
        """Override base get_all to include entity type joins.

        Args:
            filters: Optional dictionary of filters to apply

        Returns:
            List of partners matching the filters

        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        try:
            self._logger.debug(f"Fetching all partners with filters: {filters}")

            query = self._client.table(self._table_name).select("*, entity_types(name)")

            # Apply filters if provided
            if filters:
                sanitized_filters = self._sanitize_filters(filters)
                for key, value in sanitized_filters.items():
                    query = query.eq(key, value)

            response = query.order("name").execute()

            partners = []
            for row in response.data:
                # Flatten the joined data
                if row.get("entity_types"):
                    row["entity_type_name"] = row["entity_types"]["name"]

                db_model = PartnerModel.from_database_row(row)
                partner = db_model.to_domain()
                partners.append(partner)

            self._logger.debug(f"Successfully retrieved {len(partners)} partners")
            return partners

        except APIError as e:
            self._logger.error(f"Supabase API error retrieving partners: {e}")
            raise RepositoryError(f"Failed to retrieve partners: {str(e)}") from e
        except Exception as e:
            self._logger.error(f"Unexpected error retrieving partners: {e}")
            raise RepositoryError(
                f"Unexpected error retrieving partners: {str(e)}"
            ) from e

    async def get_by_id(self, entity_id: str) -> Optional[Partner]:
        """Override base get_by_id to include entity type joins.

        Args:
            entity_id: The unique identifier of the partner

        Returns:
            The partner if found, None otherwise

        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        try:
            self._validate_entity_id(entity_id)

            self._logger.debug(f"Fetching partner with ID: {entity_id}")

            response = (
                self._client.table(self._table_name)
                .select("*, entity_types(name)")
                .eq("id", entity_id)
                .execute()
            )

            if not response.data:
                self._logger.debug(f"No partner found with ID: {entity_id}")
                return None

            # Flatten the joined data
            row = response.data[0]
            if row.get("entity_types"):
                row["entity_type_name"] = row["entity_types"]["name"]

            db_model = PartnerModel.from_database_row(row)
            partner = db_model.to_domain()

            self._logger.debug(f"Successfully retrieved partner with ID: {entity_id}")
            return partner

        except APIError as e:
            self._logger.error(
                f"Supabase API error retrieving partner {entity_id}: {e}"
            )
            raise RepositoryError(f"Failed to retrieve partner: {str(e)}") from e
        except Exception as e:
            self._logger.error(f"Unexpected error retrieving partner {entity_id}: {e}")
            raise RepositoryError(
                f"Unexpected error retrieving partner: {str(e)}"
            ) from e
