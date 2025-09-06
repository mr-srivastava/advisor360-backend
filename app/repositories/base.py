"""
Base repository interface and implementation for data access layer.

This module provides the abstract base repository interface that defines
common CRUD operations and a base implementation with shared functionality.
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional, Dict, Any
from datetime import datetime


# Generic type for domain entities
T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """
    Abstract base repository interface defining common CRUD operations.
    
    This interface follows the Repository pattern to abstract data access logic
    and provide a consistent interface for all entity repositories.
    """
    
    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[T]:
        """
        Retrieve an entity by its unique identifier.
        
        Args:
            entity_id: The unique identifier of the entity
            
        Returns:
            The entity if found, None otherwise
            
        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        pass
    
    @abstractmethod
    async def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[T]:
        """
        Retrieve all entities, optionally filtered.
        
        Args:
            filters: Optional dictionary of filters to apply
            
        Returns:
            List of entities matching the filters
            
        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        pass
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        """
        Create a new entity in the data store.
        
        Args:
            entity: The entity to create
            
        Returns:
            The created entity with any generated fields populated
            
        Raises:
            RepositoryError: If there's an error creating the entity
            ValidationError: If the entity data is invalid
        """
        pass
    
    @abstractmethod
    async def update(self, entity_id: str, entity: T) -> T:
        """
        Update an existing entity in the data store.
        
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
        pass
    
    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        """
        Delete an entity from the data store.
        
        Args:
            entity_id: The unique identifier of the entity to delete
            
        Returns:
            True if the entity was deleted, False if it didn't exist
            
        Raises:
            RepositoryError: If there's an error deleting the entity
        """
        pass
    
    @abstractmethod
    async def exists(self, entity_id: str) -> bool:
        """
        Check if an entity exists in the data store.
        
        Args:
            entity_id: The unique identifier of the entity
            
        Returns:
            True if the entity exists, False otherwise
            
        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        pass
    
    @abstractmethod
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count entities in the data store, optionally filtered.
        
        Args:
            filters: Optional dictionary of filters to apply
            
        Returns:
            The number of entities matching the filters
            
        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        pass


class BaseRepositoryImpl(BaseRepository[T]):
    """
    Base repository implementation providing common functionality.
    
    This class provides shared functionality that can be used by concrete
    repository implementations to reduce code duplication.
    """
    
    def __init__(self):
        """Initialize the base repository."""
        self._created_at = datetime.now()
    
    def _validate_entity_id(self, entity_id: str) -> None:
        """
        Validate that an entity ID is not empty.
        
        Args:
            entity_id: The entity ID to validate
            
        Raises:
            ValueError: If the entity ID is empty or None
        """
        if not entity_id or not entity_id.strip():
            raise ValueError("Entity ID cannot be empty")
    
    def _validate_entity(self, entity: T) -> None:
        """
        Validate that an entity is not None.
        
        Args:
            entity: The entity to validate
            
        Raises:
            ValueError: If the entity is None
        """
        if entity is None:
            raise ValueError("Entity cannot be None")
    
    def _build_filter_query(self, base_filters: Dict[str, Any], 
                           additional_filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Build a combined filter query from base and additional filters.
        
        Args:
            base_filters: Base filters to apply
            additional_filters: Additional filters to merge
            
        Returns:
            Combined filter dictionary
        """
        combined_filters = base_filters.copy()
        if additional_filters:
            combined_filters.update(additional_filters)
        return combined_filters
    
    def _sanitize_filters(self, filters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Sanitize and validate filter parameters.
        
        Args:
            filters: Raw filter dictionary
            
        Returns:
            Sanitized filter dictionary
        """
        if not filters:
            return {}
        
        sanitized = {}
        for key, value in filters.items():
            # Skip None values and empty strings
            if value is not None and value != "":
                # Convert string representations of booleans
                if isinstance(value, str):
                    if value.lower() in ('true', 'false'):
                        sanitized[key] = value.lower() == 'true'
                    else:
                        sanitized[key] = value.strip()
                else:
                    sanitized[key] = value
        
        return sanitized
    
    async def get_by_ids(self, entity_ids: List[str]) -> List[T]:
        """
        Retrieve multiple entities by their IDs.
        
        This is a convenience method that calls get_by_id for each ID.
        Concrete implementations may override this for better performance.
        
        Args:
            entity_ids: List of entity IDs to retrieve
            
        Returns:
            List of found entities (may be fewer than requested if some don't exist)
        """
        entities = []
        for entity_id in entity_ids:
            entity = await self.get_by_id(entity_id)
            if entity:
                entities.append(entity)
        return entities
    
    async def create_many(self, entities: List[T]) -> List[T]:
        """
        Create multiple entities in the data store.
        
        This is a convenience method that calls create for each entity.
        Concrete implementations may override this for better performance.
        
        Args:
            entities: List of entities to create
            
        Returns:
            List of created entities
        """
        created_entities = []
        for entity in entities:
            created_entity = await self.create(entity)
            created_entities.append(created_entity)
        return created_entities
    
    async def delete_many(self, entity_ids: List[str]) -> int:
        """
        Delete multiple entities from the data store.
        
        This is a convenience method that calls delete for each ID.
        Concrete implementations may override this for better performance.
        
        Args:
            entity_ids: List of entity IDs to delete
            
        Returns:
            Number of entities successfully deleted
        """
        deleted_count = 0
        for entity_id in entity_ids:
            if await self.delete(entity_id):
                deleted_count += 1
        return deleted_count