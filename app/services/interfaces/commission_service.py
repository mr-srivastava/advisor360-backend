"""
Commission service interface defining business logic operations for commissions.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import date
from ...domain.commission import Commission
from ...domain.value_objects.financial_year import FinancialYear
from ...domain.value_objects.money import Money


class ICommissionService(ABC):
    """
    Interface for commission service defining business logic operations.
    
    Encapsulates all commission-related business rules and operations,
    coordinating between repositories and providing high-level functionality
    for the API layer.
    """
    
    @abstractmethod
    async def get_all_commissions(self) -> List[Commission]:
        """
        Retrieve all commissions in the system.
        
        Returns:
            List of all commissions
            
        Raises:
            ExternalServiceError: If there's an error retrieving commissions
        """
        pass
    
    @abstractmethod
    async def get_commission_by_id(self, commission_id: str) -> Commission:
        """
        Retrieve a specific commission by ID.
        
        Args:
            commission_id: The unique identifier of the commission
            
        Returns:
            The commission if found
            
        Raises:
            CommissionNotFound: If commission doesn't exist
            ExternalServiceError: If there's an error retrieving the commission
        """
        pass
    
    @abstractmethod
    async def get_commissions_by_partner(self, partner_id: str) -> List[Commission]:
        """
        Retrieve all commissions for a specific partner.
        
        Args:
            partner_id: The unique identifier of the partner
            
        Returns:
            List of commissions for the partner
            
        Raises:
            PartnerNotFound: If partner doesn't exist
            ExternalServiceError: If there's an error retrieving commissions
        """
        pass
    
    @abstractmethod
    async def get_commissions_by_financial_year(self, financial_year: str) -> List[Commission]:
        """
        Retrieve all commissions for a specific financial year.
        
        Args:
            financial_year: The financial year string (e.g., "FY24-25")
            
        Returns:
            List of commissions in the financial year
            
        Raises:
            ExternalServiceError: If there's an error retrieving commissions
        """
        pass
    
    @abstractmethod
    async def get_commissions_with_partners(self) -> List[Dict]:
        """
        Retrieve all commissions with their associated partner information.
        
        Returns:
            List of commission dictionaries with partner details
            
        Raises:
            ExternalServiceError: If there's an error retrieving data
        """
        pass
    
    @abstractmethod
    async def create_commission(self, partner_id: str, amount: float, 
                              transaction_date: date, description: Optional[str] = None) -> Commission:
        """
        Create a new commission.
        
        Args:
            partner_id: The unique identifier of the partner
            amount: The commission amount
            transaction_date: The date of the transaction
            description: Optional description
            
        Returns:
            The created commission
            
        Raises:
            PartnerNotFound: If partner doesn't exist
            ValidationError: If input data is invalid
            ExternalServiceError: If there's an error creating the commission
        """
        pass
    
    @abstractmethod
    async def update_commission(self, commission_id: str, amount: Optional[float] = None,
                              description: Optional[str] = None) -> Commission:
        """
        Update an existing commission.
        
        Args:
            commission_id: The unique identifier of the commission
            amount: Optional new amount
            description: Optional new description
            
        Returns:
            The updated commission
            
        Raises:
            CommissionNotFound: If commission doesn't exist
            ValidationError: If input data is invalid
            ExternalServiceError: If there's an error updating the commission
        """
        pass
    
    @abstractmethod
    async def delete_commission(self, commission_id: str) -> bool:
        """
        Delete a commission.
        
        Args:
            commission_id: The unique identifier of the commission
            
        Returns:
            True if deleted successfully
            
        Raises:
            CommissionNotFound: If commission doesn't exist
            ExternalServiceError: If there's an error deleting the commission
        """
        pass
    
    @abstractmethod
    async def get_total_commissions(self) -> float:
        """
        Get total commission amount across all time.
        
        Returns:
            Total commission amount
            
        Raises:
            ExternalServiceError: If there's an error calculating totals
        """
        pass
    
    @abstractmethod
    async def get_total_commissions_by_month(self, month: str, year: int) -> float:
        """
        Get total commission amount for a specific month and year.
        
        Args:
            month: The month name (e.g., "January")
            year: The year
            
        Returns:
            Total commission amount for the month
            
        Raises:
            ExternalServiceError: If there's an error calculating totals
        """
        pass
    
    @abstractmethod
    async def get_total_commissions_by_financial_year(self, financial_year: str) -> float:
        """
        Get total commission amount for a specific financial year.
        
        Args:
            financial_year: The financial year string (e.g., "FY24-25")
            
        Returns:
            Total commission amount for the financial year
            
        Raises:
            ExternalServiceError: If there's an error calculating totals
        """
        pass
    
    @abstractmethod
    async def get_monthly_analytics(self) -> List[Dict]:
        """
        Get monthly commission analytics for the last 6 months.
        
        Returns:
            List of monthly analytics data
            
        Raises:
            ExternalServiceError: If there's an error generating analytics
        """
        pass
    
    @abstractmethod
    async def get_recent_commissions(self, limit: int = 10) -> List[Commission]:
        """
        Get the most recent commissions.
        
        Args:
            limit: Maximum number of commissions to return
            
        Returns:
            List of recent commissions
            
        Raises:
            ExternalServiceError: If there's an error retrieving commissions
        """
        pass
    
    @abstractmethod
    async def search_commissions(self, search_term: str) -> List[Commission]:
        """
        Search commissions by description.
        
        Args:
            search_term: The text to search for
            
        Returns:
            List of matching commissions
            
        Raises:
            ExternalServiceError: If there's an error searching commissions
        """
        pass