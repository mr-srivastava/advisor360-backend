"""Base Supabase repository implementation providing common database operations."""

import logging
from typing import Any, Generic, Optional, TypeVar

from postgrest.exceptions import APIError
from supabase import Client

from ...core.exceptions.repository_exceptions import (
    ConnectionError,
    NotFoundError,
    RepositoryError,
    ValidationError,
)
from ..base import BaseRepositoryImpl

# Generic types
T = TypeVar("T")  # Domain model type
M = TypeVar("M")  # Database model type

logger = logging.getLogger(__name__)


class BaseSupabaseRepository(BaseRepositoryImpl[T], Generic[T, M]):
    """Base Supabase repository implementation providing common database operations.

    This class provides shared functionality for all Supabase repositories including
    connection management, error handling, and common CRUD operations.
    """

    def __init__(self, supabase_client: Client, table_name: str, model_class: type[M]):
        """Initialize the base Supabase repository.

        Args:
            supabase_client: Supabase client instance
            table_name: Name of the database table
            model_class: Database model class for conversions
        """
        super().__init__()
        self._client = supabase_client
        self._table_name = table_name
        self._model_class = model_class
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def get_by_id(self, entity_id: str) -> Optional[T]:
        """Retrieve an entity by its unique identifier.

        Args:
            entity_id: The unique identifier of the entity

        Returns:
            The entity if found, None otherwise

        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        try:
            self._validate_entity_id(entity_id)

            self._logger.debug(f"Fetching {self._table_name} with ID: {entity_id}")

            response = (
                self._client.table(self._table_name)
                .select("*")
                .eq("id", entity_id)
                .execute()
            )

            if not response.data:
                self._logger.debug(f"No {self._table_name} found with ID: {entity_id}")
                return None

            # Convert database row to domain model
            db_model = self._model_class.from_database_row(response.data[0])
            domain_model = db_model.to_domain()

            self._logger.debug(
                f"Successfully retrieved {self._table_name} with ID: {entity_id}"
            )
            return domain_model

        except APIError as e:
            self._logger.error(
                f"Supabase API error retrieving {self._table_name} {entity_id}: {e}"
            )
            raise RepositoryError(
                f"Failed to retrieve {self._table_name}: {str(e)}"
            ) from e
        except Exception as e:
            self._logger.error(
                f"Unexpected error retrieving {self._table_name} {entity_id}: {e}"
            )
            raise RepositoryError(
                f"Unexpected error retrieving {self._table_name}: {str(e)}"
            ) from e

    async def get_all(self, filters: Optional[dict[str, Any]] = None) -> list[T]:
        """Retrieve all entities, optionally filtered.
        Handles Supabase's 1000 record limit by paginating through all results.

        Args:
            filters: Optional dictionary of filters to apply

        Returns:
            List of entities matching the filters

        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        try:
            self._logger.debug(
                f"Fetching all {self._table_name} with filters: {filters}"
            )

            all_domain_models = []
            page_size = 1000  # Supabase default limit
            offset = 0

            while True:
                query = self._client.table(self._table_name).select("*")

                # Apply filters if provided
                if filters:
                    sanitized_filters = self._sanitize_filters(filters)
                    for key, value in sanitized_filters.items():
                        query = query.eq(key, value)

                # Add pagination
                query = query.range(offset, offset + page_size - 1)

                response = query.execute()

                if not response.data:
                    break

                # Convert database rows to domain models
                for row in response.data:
                    db_model = self._model_class.from_database_row(row)
                    domain_model = db_model.to_domain()
                    all_domain_models.append(domain_model)

                # If we got less than page_size records, we've reached the end
                if len(response.data) < page_size:
                    break

                offset += page_size

            self._logger.debug(
                f"Successfully retrieved {len(all_domain_models)} {self._table_name} records"
            )
            return all_domain_models

        except APIError as e:
            self._logger.error(f"Supabase API error retrieving {self._table_name}: {e}")
            raise RepositoryError(
                f"Failed to retrieve {self._table_name}: {str(e)}"
            ) from e
        except Exception as e:
            self._logger.error(f"Unexpected error retrieving {self._table_name}: {e}")
            raise RepositoryError(
                f"Unexpected error retrieving {self._table_name}: {str(e)}"
            ) from e

    async def get_all_ordered(
        self,
        order_by: str = "created_at",
        ascending: bool = False,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[T]:
        """Retrieve all entities with ordering, handling Supabase's 1000 record limit.

        Args:
            order_by: Column to order by (default: created_at)
            ascending: Whether to sort in ascending order (default: False for descending)
            filters: Optional dictionary of filters to apply

        Returns:
            List of entities matching the filters, ordered as specified

        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        try:
            self._logger.debug(
                f"Fetching all {self._table_name} ordered by {order_by} (asc={ascending}) with filters: {filters}"
            )

            all_domain_models = []
            page_size = 1000  # Supabase default limit
            offset = 0

            while True:
                query = self._client.table(self._table_name).select("*")

                # Apply filters if provided
                if filters:
                    sanitized_filters = self._sanitize_filters(filters)
                    for key, value in sanitized_filters.items():
                        query = query.eq(key, value)

                # Add ordering
                query = query.order(order_by, desc=not ascending)

                # Add pagination
                query = query.range(offset, offset + page_size - 1)

                response = query.execute()

                if not response.data:
                    break

                # Convert database rows to domain models
                for row in response.data:
                    db_model = self._model_class.from_database_row(row)
                    domain_model = db_model.to_domain()
                    all_domain_models.append(domain_model)

                # If we got less than page_size records, we've reached the end
                if len(response.data) < page_size:
                    break

                offset += page_size

            self._logger.debug(
                f"Successfully retrieved {len(all_domain_models)} ordered {self._table_name} records"
            )
            return all_domain_models

        except APIError as e:
            self._logger.error(
                f"Supabase API error retrieving ordered {self._table_name}: {e}"
            )
            raise RepositoryError(
                f"Failed to retrieve ordered {self._table_name}: {str(e)}"
            ) from e
        except Exception as e:
            self._logger.error(
                f"Unexpected error retrieving ordered {self._table_name}: {e}"
            )
            raise RepositoryError(
                f"Unexpected error retrieving ordered {self._table_name}: {str(e)}"
            ) from e

    async def create(self, entity: T) -> T:
        """Create a new entity in the data store.

        Args:
            entity: The entity to create

        Returns:
            The created entity with any generated fields populated

        Raises:
            RepositoryError: If there's an error creating the entity
            ValidationError: If the entity data is invalid
        """
        try:
            self._validate_entity(entity)

            # Convert domain model to database model
            db_model = self._model_class.from_domain(entity)
            data = db_model.to_database_dict()

            self._logger.debug(f"Creating {self._table_name} with data: {data}")

            response = self._client.table(self._table_name).insert(data).execute()

            if not response.data:
                raise RepositoryError(
                    f"Failed to create {self._table_name}: No data returned"
                )

            # Convert created record back to domain model
            created_db_model = self._model_class.from_database_row(response.data[0])
            created_domain_model = created_db_model.to_domain()

            self._logger.debug(
                f"Successfully created {self._table_name} with ID: {created_domain_model.id}"
            )
            return created_domain_model

        except APIError as e:
            self._logger.error(f"Supabase API error creating {self._table_name}: {e}")
            if "duplicate key" in str(e).lower():
                raise ValidationError(
                    f"{self._table_name} with this ID already exists"
                ) from e
            raise RepositoryError(
                f"Failed to create {self._table_name}: {str(e)}"
            ) from e
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Unexpected error creating {self._table_name}: {e}")
            raise RepositoryError(
                f"Unexpected error creating {self._table_name}: {str(e)}"
            ) from e

    async def update(self, entity_id: str, entity: T) -> T:
        """Update an existing entity in the data store.

        Args:
            entity_id: The unique identifier of the entity to update
            entity: The updated entity data

        Returns:
            The updated entity

        Raises:
            RepositoryError: If there's an error updating the entity
            NotFoundError: If the entity doesn't exist
            ValidationError: If the entity data is invalid
        """
        try:
            self._validate_entity_id(entity_id)
            self._validate_entity(entity)

            # Check if entity exists
            if not await self.exists(entity_id):
                raise NotFoundError(f"{self._table_name} with ID {entity_id} not found")

            # Convert domain model to database model
            db_model = self._model_class.from_domain(entity)
            data = db_model.to_database_dict()

            # Remove ID from update data to avoid conflicts
            data.pop("id", None)

            self._logger.debug(
                f"Updating {self._table_name} {entity_id} with data: {data}"
            )

            response = (
                self._client.table(self._table_name)
                .update(data)
                .eq("id", entity_id)
                .execute()
            )

            if not response.data:
                raise RepositoryError(
                    f"Failed to update {self._table_name}: No data returned"
                )

            # Convert updated record back to domain model
            updated_db_model = self._model_class.from_database_row(response.data[0])
            updated_domain_model = updated_db_model.to_domain()

            self._logger.debug(
                f"Successfully updated {self._table_name} with ID: {entity_id}"
            )
            return updated_domain_model

        except (NotFoundError, ValidationError):
            raise
        except APIError as e:
            self._logger.error(
                f"Supabase API error updating {self._table_name} {entity_id}: {e}"
            )
            raise RepositoryError(
                f"Failed to update {self._table_name}: {str(e)}"
            ) from e
        except Exception as e:
            self._logger.error(
                f"Unexpected error updating {self._table_name} {entity_id}: {e}"
            )
            raise RepositoryError(
                f"Unexpected error updating {self._table_name}: {str(e)}"
            ) from e

    async def delete(self, entity_id: str) -> bool:
        """Delete an entity from the data store.

        Args:
            entity_id: The unique identifier of the entity to delete

        Returns:
            True if the entity was deleted, False if it didn't exist

        Raises:
            RepositoryError: If there's an error deleting the entity
        """
        try:
            self._validate_entity_id(entity_id)

            self._logger.debug(f"Deleting {self._table_name} with ID: {entity_id}")

            response = (
                self._client.table(self._table_name)
                .delete()
                .eq("id", entity_id)
                .execute()
            )

            # Check if any rows were affected
            deleted = len(response.data) > 0

            if deleted:
                self._logger.debug(
                    f"Successfully deleted {self._table_name} with ID: {entity_id}"
                )
            else:
                self._logger.debug(
                    f"No {self._table_name} found to delete with ID: {entity_id}"
                )

            return deleted

        except APIError as e:
            self._logger.error(
                f"Supabase API error deleting {self._table_name} {entity_id}: {e}"
            )
            raise RepositoryError(
                f"Failed to delete {self._table_name}: {str(e)}"
            ) from e
        except Exception as e:
            self._logger.error(
                f"Unexpected error deleting {self._table_name} {entity_id}: {e}"
            )
            raise RepositoryError(
                f"Unexpected error deleting {self._table_name}: {str(e)}"
            ) from e

    async def exists(self, entity_id: str) -> bool:
        """Check if an entity exists in the data store.

        Args:
            entity_id: The unique identifier of the entity

        Returns:
            True if the entity exists, False otherwise

        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        try:
            self._validate_entity_id(entity_id)

            response = (
                self._client.table(self._table_name)
                .select("id")
                .eq("id", entity_id)
                .execute()
            )

            return len(response.data) > 0

        except APIError as e:
            self._logger.error(
                f"Supabase API error checking existence of {self._table_name} {entity_id}: {e}"
            )
            raise RepositoryError(
                f"Failed to check {self._table_name} existence: {str(e)}"
            ) from e
        except Exception as e:
            self._logger.error(
                f"Unexpected error checking existence of {self._table_name} {entity_id}: {e}"
            )
            raise RepositoryError(
                f"Unexpected error checking {self._table_name} existence: {str(e)}"
            ) from e

    async def count(self, filters: Optional[dict[str, Any]] = None) -> int:
        """Count entities in the data store, optionally filtered.

        Args:
            filters: Optional dictionary of filters to apply

        Returns:
            The number of entities matching the filters

        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        try:
            query = self._client.table(self._table_name).select("id", count="exact")

            # Apply filters if provided
            if filters:
                sanitized_filters = self._sanitize_filters(filters)
                for key, value in sanitized_filters.items():
                    query = query.eq(key, value)

            response = query.execute()

            return response.count or 0

        except APIError as e:
            self._logger.error(f"Supabase API error counting {self._table_name}: {e}")
            raise RepositoryError(
                f"Failed to count {self._table_name}: {str(e)}"
            ) from e
        except Exception as e:
            self._logger.error(f"Unexpected error counting {self._table_name}: {e}")
            raise RepositoryError(
                f"Unexpected error counting {self._table_name}: {str(e)}"
            ) from e

    def _handle_connection_error(self, error: Exception) -> None:
        """Handle connection-related errors."""
        self._logger.error(f"Connection error: {error}")
        raise ConnectionError(f"Database connection failed: {str(error)}") from error

    def _build_select_query(self, columns: str = "*") -> Any:
        """Build a base select query for the table."""
        return self._client.table(self._table_name).select(columns)

    def _execute_query_with_retry(self, query, max_retries: int = 3):
        """Execute query with retry logic for transient failures."""
        for attempt in range(max_retries):
            try:
                return query.execute()
            except APIError as e:
                if attempt == max_retries - 1:
                    raise
                if "timeout" in str(e).lower() or "connection" in str(e).lower():
                    self._logger.warning(
                        f"Query attempt {attempt + 1} failed, retrying: {e}"
                    )
                    continue
                raise
