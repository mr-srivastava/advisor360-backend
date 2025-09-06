"""
Partner service interface defining business logic operations for partners.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from ...domain.partner import Partner, EntityType


class IPartnerService(ABC):
    """
    Interface for partner service defining business logic operations.
    
    Encapsulates all partner-related business rules and operations,
    coordinating between repositories and providing high-level functionality
    for the API layer.
    """
    
    @abstractmethod
    async def get_all_partners(self) -> List[Partner]:
        """
        Retrieve all partners in the system.
        
        Returns:
            List of all partners
            
        Raises:
            ServiceError: If there's an error retrieving partners
        """
        pass
    
    @abstractmethod
    async def get_partner_by_id(self, partner_id: str) -> Partner:
        """
        Retrieve a specific partner by ID.
        
        Args:
            partner_id: The unique identifier of the partner
            
        Returns:
            The partner if found
            
        Raises:
            PartnerNotFound: If partner doesn't exist
            ServiceError: If there's an error retrieving the partner
        """
        pass
    
    @abstractmethod
    async def get_partner_by_name(self, name: str) -> Optional[Partner]:
        """
        Retrieve a partner by exact name.
        
        Args:
            name: The exact name of the partner
            
        Returns:
            The partner if found, None otherwise
            
        Raises:
            ServiceError: If there's an error retrieving the partner
        """
        pass
    
    @abstractmethod
    async def get_partners_by_entity_type(self, entity_type: EntityType) -> List[Partner]:
        """
        Retrieve all partners of a specific entity type.
        
        Args:
            entity_type: The entity type to filter by
            
        Returns:
            List of partners with the specified entity type
            
        Raises:
            ServiceError: If there's an error retrieving partners
        """
        pass
    
    @abstractmethod
    async def create_partner(self, name: str, entity_type: EntityType) -> Partner:
        """
        Create a new partner.
        
        Args:
            name: The partner name
            entity_type: The entity type
            
        Returns:
            The created partner
            
        Raises:
            ValidationError: If input data is invalid
            DuplicatePartnerError: If partner name already exists
            ServiceError: If there's an error creating the partner
        """
        pass
    
    @abstractmethod
    async def update_partner(self, partner_id: str, name: Optional[str] = None,
                           entity_type: Optional[EntityType] = None) -> Partner:
        """
        Update an existing partner.
        
        Args:
            partner_id: The unique identifier of the partner
            name: Optional new name
            entity_type: Optional new entity type
            
        Returns:
            The updated partner
            
        Raises:
            PartnerNotFound: If partner doesn't exist
            ValidationError: If input data is invalid
            DuplicatePartnerError: If new name already exists
            ServiceError: If there's an error updating the partner
        """
        pass
    
    @abstractmethod
    async def delete_partner(self, partner_id: str) -> bool:
        """
        Delete a partner.
        
        Args:
            partner_id: The unique identifier of the partner
            
        Returns:
            True if deleted successfully
            
        Raises:
            PartnerNotFound: If partner doesn't exist
            PartnerHasCommissionsError: If partner has associated commissions
            ServiceError: If there's an error deleting the partner
        """
        pass
    
    @abstractmethod
    async def search_partners(self, search_term: str) -> List[Partner]:
        """
        Search partners by name.
        
        Args:
            search_term: The text to search for in partner names
            
        Returns:
            List of matching partners
            
        Raises:
            ServiceError: If there's an error searching partners
        """
        pass
    
    @abstractmethod
    async def get_active_partners(self) -> List[Partner]:
        """
        Retrieve all active partners.
        
        Returns:
            List of active partners
            
        Raises:
            ServiceError: If there's an error retrieving partners
        """
        pass
    
    @abstractmethod
    async def get_partners_with_commissions(self) -> List[Partner]:
        """
        Retrieve partners who have at least one commission.
        
        Returns:
            List of partners with commissions
            
        Raises:
            ServiceError: If there's an error retrieving partners
        """
        pass
    
    @abstractmethod
    async def get_partners_without_commissions(self) -> List[Partner]:
        """
        Retrieve partners who have no commissions.
        
        Returns:
            List of partners without commissions
            
        Raises:
            ServiceError: If there's an error retrieving partners
        """
        pass
    
    @abstractmethod
    async def get_entity_type_statistics(self) -> Dict[str, int]:
        """
        Get count of partners by entity type.
        
        Returns:
            Dictionary mapping entity type names to partner counts
            
        Raises:
            ServiceError: If there's an error calculating statistics
        """
        pass
    
    @abstractmethod
    async def validate_partner_name(self, name: str, exclude_id: Optional[str] = None) -> bool:
        """
        Validate if a partner name is available.
        
        Args:
            name: The name to validate
            exclude_id: Optional partner ID to exclude from validation (for updates)
            
        Returns:
            True if name is available, False if already exists
            
        Raises:
            ServiceError: If there's an error validating the name
        """
        pass
    
    @abstractmethod
    async def get_recently_created_partners(self, limit: int = 10) -> List[Partner]:
        """
        Get the most recently created partners.
        
        Args:
            limit: Maximum number of partners to return
            
        Returns:
            List of recent partners
            
        Raises:
            ServiceError: If there's an error retrieving partners
        """
        pass