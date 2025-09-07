"""
Partner repository interface defining partner-specific data access operations.
"""

from abc import abstractmethod
from typing import List, Optional, Dict, Any
from ..base import BaseRepository
from ...domain.partner import Partner, EntityType


class IPartnerRepository(BaseRepository[Partner]):
    """
    Interface for partner repository defining partner-specific operations.
    
    Extends the base repository interface with partner-specific query methods
    for business logic requirements like entity type filtering, name-based
    searches, and partner analytics operations.
    """
    
    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Partner]:
        """
        Retrieve a partner by their exact name.
        
        Args:
            name: The exact name of the partner
            
        Returns:
            The partner if found, None otherwise
            
        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        pass
    
    @abstractmethod
    async def get_by_entity_type(self, entity_type: EntityType) -> List[Partner]:
        """
        Retrieve all partners of a specific entity type.
        
        Args:
            entity_type: The entity type to filter by
            
        Returns:
            List of partners with the specified entity type
            
        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        pass
    
    @abstractmethod
    async def search_by_name(self, search_term: str) -> List[Partner]:
        """
        Search partners by name using partial matching.
        
        Args:
            search_term: The text to search for in partner names
            
        Returns:
            List of partners with names containing the search term
            
        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        pass
    
    @abstractmethod
    async def get_active_partners(self) -> List[Partner]:
        """
        Retrieve all active partners.
        
        Returns:
            List of active partners
            
        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        pass
    
    @abstractmethod
    async def get_partners_with_commissions(self) -> List[Partner]:
        """
        Retrieve partners who have at least one commission.
        
        Returns:
            List of partners with commissions
            
        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        pass
    
    @abstractmethod
    async def get_partners_without_commissions(self) -> List[Partner]:
        """
        Retrieve partners who have no commissions.
        
        Returns:
            List of partners without commissions
            
        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        pass
    
    @abstractmethod
    async def get_entity_type_counts(self) -> Dict[EntityType, int]:
        """
        Get count of partners by entity type.
        
        Returns:
            Dictionary mapping entity types to partner counts
            
        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        pass
    
    @abstractmethod
    async def name_exists(self, name: str, exclude_id: Optional[str] = None) -> bool:
        """
        Check if a partner name already exists.
        
        Args:
            name: The name to check
            exclude_id: Optional partner ID to exclude from the check (for updates)
            
        Returns:
            True if the name exists, False otherwise
            
        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        pass
    
    @abstractmethod
    async def get_recently_created(self, limit: int = 10) -> List[Partner]:
        """
        Retrieve the most recently created partners.
        
        Args:
            limit: Maximum number of partners to return
            
        Returns:
            List of recent partners ordered by creation date (newest first)
            
        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        pass
    
    @abstractmethod
    async def get_recently_updated(self, limit: int = 10) -> List[Partner]:
        """
        Retrieve the most recently updated partners.
        
        Args:
            limit: Maximum number of partners to return
            
        Returns:
            List of recently updated partners ordered by update date (newest first)
            
        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        pass