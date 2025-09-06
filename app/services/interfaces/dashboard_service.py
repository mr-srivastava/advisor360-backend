"""
Dashboard service interface defining business logic operations for analytics and reporting.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class IDashboardService(ABC):
    """
    Interface for dashboard service defining analytics and reporting operations.
    
    Encapsulates all dashboard-related business logic, providing high-level
    analytics and reporting functionality for the API layer.
    """
    
    @abstractmethod
    async def get_overview_statistics(self) -> List[Dict[str, Any]]:
        """
        Get overview statistics for the dashboard.
        
        Returns:
            List of statistics including total commission, current month commission,
            financial year commission, and growth rate
            
        Raises:
            ServiceError: If there's an error calculating statistics
        """
        pass
    
    @abstractmethod
    async def get_recent_activities(self) -> Dict[str, Any]:
        """
        Get recent activities including recent commissions and monthly data.
        
        Returns:
            Dictionary containing recent commissions and monthly commission data
            
        Raises:
            ServiceError: If there's an error retrieving activities
        """
        pass
    
    @abstractmethod
    async def get_available_financial_years(self) -> List[str]:
        """
        Get all available financial years from the system.
        
        Returns:
            List of financial year strings (e.g., ["FY23-24", "FY24-25"])
            
        Raises:
            ServiceError: If there's an error retrieving financial years
        """
        pass
    
    @abstractmethod
    async def calculate_financial_year_metrics(self, financial_year: str) -> Dict[str, Any]:
        """
        Calculate key metrics for a specific financial year.
        
        Args:
            financial_year: The financial year string (e.g., "FY24-25")
            
        Returns:
            Dictionary containing FY metrics including total, YoY growth, and commission count
            
        Raises:
            FinancialYearNotFound: If financial year doesn't exist
            ServiceError: If there's an error calculating metrics
        """
        pass
    
    @abstractmethod
    async def get_monthly_commissions_by_financial_year(self, financial_year: str) -> List[Dict[str, Any]]:
        """
        Get monthly commission breakdown for a specific financial year.
        
        Args:
            financial_year: The financial year string (e.g., "FY24-25")
            
        Returns:
            List of monthly commission data for the financial year
            
        Raises:
            FinancialYearNotFound: If financial year doesn't exist
            ServiceError: If there's an error retrieving monthly data
        """
        pass
    
    @abstractmethod
    async def get_entity_performance_by_financial_year(self, financial_year: str) -> List[Dict[str, Any]]:
        """
        Get entity performance breakdown for a specific financial year.
        
        Args:
            financial_year: The financial year string (e.g., "FY24-25")
            
        Returns:
            List of entity performance data including totals and percentages
            
        Raises:
            FinancialYearNotFound: If financial year doesn't exist
            ServiceError: If there's an error retrieving entity performance
        """
        pass
    
    @abstractmethod
    async def get_growth_analytics(self, financial_year: str) -> Dict[str, Any]:
        """
        Get growth analytics comparing current and previous financial years.
        
        Args:
            financial_year: The financial year string (e.g., "FY24-25")
            
        Returns:
            Dictionary containing growth metrics and comparisons
            
        Raises:
            FinancialYearNotFound: If financial year doesn't exist
            ServiceError: If there's an error calculating growth analytics
        """
        pass
    
    @abstractmethod
    async def get_commission_trends(self, months: int = 12) -> List[Dict[str, Any]]:
        """
        Get commission trends over the specified number of months.
        
        Args:
            months: Number of months to include in trends (default: 12)
            
        Returns:
            List of monthly trend data
            
        Raises:
            ServiceError: If there's an error calculating trends
        """
        pass
    
    @abstractmethod
    async def get_partner_performance_summary(self) -> List[Dict[str, Any]]:
        """
        Get performance summary for all partners.
        
        Returns:
            List of partner performance data including totals and rankings
            
        Raises:
            ServiceError: If there's an error calculating partner performance
        """
        pass
    
    @abstractmethod
    async def get_quarterly_breakdown(self, financial_year: str) -> List[Dict[str, Any]]:
        """
        Get quarterly commission breakdown for a financial year.
        
        Args:
            financial_year: The financial year string (e.g., "FY24-25")
            
        Returns:
            List of quarterly data for the financial year
            
        Raises:
            FinancialYearNotFound: If financial year doesn't exist
            ServiceError: If there's an error calculating quarterly breakdown
        """
        pass