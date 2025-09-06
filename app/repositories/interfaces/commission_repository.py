"""
Commission repository interface defining commission-specific data access operations.
"""

from abc import abstractmethod
from typing import List, Optional, Dict, Any
from datetime import date
from ..base import BaseRepository
from ...domain.commission import Commission
from ...domain.value_objects.financial_year import FinancialYear


class ICommissionRepository(BaseRepository[Commission]):
    """
    Interface for commission repository defining commission-specific operations.
    
    Extends the base repository interface with commission-specific query methods
    for business logic requirements like financial year filtering, partner-based
    queries, and analytics operations.
    """
    
    @abstractmethod
    async def get_by_partner_id(self, partner_id: str) -> List[Commission]:
        """
        Retrieve all commissions for a specific partner.
        
        Args:
            partner_id: The unique identifier of the partner
            
        Returns:
            List of commissions for the partner
            
        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        pass
    
    @abstractmethod
    async def get_by_financial_year(self, financial_year: FinancialYear) -> List[Commission]:
        """
        Retrieve all commissions for a specific financial year.
        
        Args:
            financial_year: The financial year to filter by
            
        Returns:
            List of commissions in the financial year
            
        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        pass
    
    @abstractmethod
    async def get_by_partner_and_financial_year(self, partner_id: str, 
                                               financial_year: FinancialYear) -> List[Commission]:
        """
        Retrieve commissions for a specific partner in a specific financial year.
        
        Args:
            partner_id: The unique identifier of the partner
            financial_year: The financial year to filter by
            
        Returns:
            List of commissions matching the criteria
            
        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        pass
    
    @abstractmethod
    async def get_by_date_range(self, start_date: date, end_date: date) -> List[Commission]:
        """
        Retrieve commissions within a specific date range.
        
        Args:
            start_date: The start date (inclusive)
            end_date: The end date (inclusive)
            
        Returns:
            List of commissions within the date range
            
        Raises:
            RepositoryError: If there's an error accessing the data store
            ValueError: If start_date is after end_date
        """
        pass
    
    @abstractmethod
    async def get_by_month_year(self, month: int, year: int) -> List[Commission]:
        """
        Retrieve commissions for a specific month and year.
        
        Args:
            month: The month (1-12)
            year: The year
            
        Returns:
            List of commissions for the specified month and year
            
        Raises:
            RepositoryError: If there's an error accessing the data store
            ValueError: If month is not between 1-12
        """
        pass
    
    @abstractmethod
    async def get_total_amount_by_partner(self, partner_id: str, 
                                        financial_year: Optional[FinancialYear] = None) -> float:
        """
        Calculate total commission amount for a partner, optionally filtered by financial year.
        
        Args:
            partner_id: The unique identifier of the partner
            financial_year: Optional financial year filter
            
        Returns:
            Total commission amount for the partner
            
        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        pass
    
    @abstractmethod
    async def get_total_amount_by_financial_year(self, financial_year: FinancialYear) -> float:
        """
        Calculate total commission amount for a financial year.
        
        Args:
            financial_year: The financial year to calculate totals for
            
        Returns:
            Total commission amount for the financial year
            
        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        pass
    
    @abstractmethod
    async def get_monthly_totals(self, financial_year: FinancialYear) -> Dict[str, float]:
        """
        Get monthly commission totals for a financial year.
        
        Args:
            financial_year: The financial year to get monthly totals for
            
        Returns:
            Dictionary mapping month names to total amounts
            
        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        pass
    
    @abstractmethod
    async def get_partner_totals(self, financial_year: Optional[FinancialYear] = None) -> Dict[str, float]:
        """
        Get commission totals by partner, optionally filtered by financial year.
        
        Args:
            financial_year: Optional financial year filter
            
        Returns:
            Dictionary mapping partner IDs to total amounts
            
        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        pass
    
    @abstractmethod
    async def get_recent_commissions(self, limit: int = 10) -> List[Commission]:
        """
        Retrieve the most recent commissions.
        
        Args:
            limit: Maximum number of commissions to return
            
        Returns:
            List of recent commissions ordered by creation date (newest first)
            
        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        pass
    
    @abstractmethod
    async def search_by_description(self, search_term: str) -> List[Commission]:
        """
        Search commissions by description text.
        
        Args:
            search_term: The text to search for in descriptions
            
        Returns:
            List of commissions with descriptions containing the search term
            
        Raises:
            RepositoryError: If there's an error accessing the data store
        """
        pass