"""
Usage examples for the standardized error handling system.

This module demonstrates how to use the new exception hierarchy,
error logging, and error handling components throughout the application.
"""

from typing import Optional
from datetime import datetime

# Import the new exception classes
from .domain_exceptions import (
    ValidationError,
    NotFoundError,
    BusinessRuleViolation,
    DuplicateError,
    PartnerNotFound,
    CommissionNotFound,
    InvalidCommissionAmount,
    FinancialYearError
)

from .infrastructure_exceptions import (
    DatabaseError,
    SupabaseError,
    ConnectionError,
    TimeoutError
)

from ..logging.error_logger import error_logger, error_context, log_exception


# Example 1: Using domain exceptions in service methods

def get_partner_by_id(partner_id: str):
    """Example service method showing proper exception usage."""
    
    # Validate input
    if not partner_id or not partner_id.strip():
        raise ValidationError(
            "Partner ID is required",
            field="partner_id",
            value=partner_id,
            validation_rule="required"
        )
    
    # Simulate partner lookup
    partner = None  # This would be actual database lookup
    
    if not partner:
        raise PartnerNotFound(partner_id)
    
    return partner


def create_commission(partner_id: str, amount: float, description: Optional[str] = None):
    """Example service method showing business rule validation."""
    
    # Validate amount
    if amount <= 0:
        raise InvalidCommissionAmount(amount)
    
    # Check if partner exists
    try:
        partner = get_partner_by_id(partner_id)
    except PartnerNotFound:
        # Re-raise with additional context
        raise PartnerNotFound(
            partner_id,
            context={"operation": "create_commission", "attempted_amount": amount}
        )
    
    # Business rule: Check if partner is active
    if not getattr(partner, 'is_active', True):
        raise BusinessRuleViolation(
            rule_name="active_partner_required",
            message=f"Cannot create commission for inactive partner: {partner_id}",
            context={"partner_id": partner_id, "partner_status": "inactive"}
        )
    
    # Simulate commission creation
    return {"id": "comm_123", "partner_id": partner_id, "amount": amount}


def delete_partner(partner_id: str):
    """Example showing business rule violations."""
    
    # Check if partner has commissions
    commission_count = 5  # This would be actual database query
    
    if commission_count > 0:
        from .domain_exceptions import PartnerHasCommissions
        raise PartnerHasCommissions(partner_id, commission_count)
    
    # Proceed with deletion
    return True


# Example 2: Using infrastructure exceptions in repository methods

def fetch_partner_from_database(partner_id: str):
    """Example repository method showing infrastructure exception usage."""
    
    try:
        # Simulate database operation
        result = None  # This would be actual Supabase call
        
        if result is None:
            raise SupabaseError(
                operation="select_partner",
                status_code=404,
                context={"partner_id": partner_id, "table": "partners"}
            )
        
        return result
        
    except Exception as e:
        # Wrap unexpected database errors
        raise DatabaseError(
            operation="fetch_partner",
            table="partners",
            context={"partner_id": partner_id},
            original_error=e
        )


def connect_to_database():
    """Example showing connection error handling."""
    
    try:
        # Simulate connection attempt
        connected = False  # This would be actual connection logic
        
        if not connected:
            raise ConnectionError(
                service="supabase",
                host="your-project.supabase.co",
                port=443,
                context={"connection_timeout": 30}
            )
        
    except TimeoutError as e:
        # Convert timeout to connection error with context
        raise ConnectionError(
            service="supabase",
            message="Database connection timed out",
            original_error=e
        )


# Example 3: Using the error logging system

def example_service_with_logging():
    """Example showing proper error logging usage."""
    
    try:
        # Some operation that might fail
        partner_id = "invalid_id"
        partner = get_partner_by_id(partner_id)
        
    except ValidationError as e:
        # Log validation errors with context
        error_logger.log_validation_error(
            e,
            field=e.field,
            value=e.value,
            validation_rule=e.validation_rule
        )
        raise  # Re-raise for proper handling
        
    except PartnerNotFound as e:
        # Log not found errors
        error_logger.log_error(e, severity="WARNING")
        raise
        
    except BusinessRuleViolation as e:
        # Log business rule violations
        error_logger.log_business_rule_violation(
            e,
            rule_name=e.rule_name,
            entity_type="Partner",
            entity_id=partner_id
        )
        raise
        
    except Exception as e:
        # Log unexpected errors
        error_logger.log_critical_error(
            e,
            system_impact="Partner service unavailable",
            recovery_action="Check partner service and database connectivity"
        )
        raise


# Example 4: Using error context for request tracing

def handle_api_request(request_id: str, user_id: str):
    """Example showing error context usage in API handlers."""
    
    with error_context(request_id=request_id, user_id=user_id):
        try:
            # Process request
            result = example_service_with_logging()
            return result
            
        except Exception as e:
            # All logging within this context will include request_id and user_id
            log_exception(e, severity="ERROR", context={"api_endpoint": "/partners"})
            raise


# Example 5: Custom domain exceptions

class CustomBusinessRule(BusinessRuleViolation):
    """Example of creating custom business rule exceptions."""
    
    def __init__(self, entity_id: str, rule_details: dict, **kwargs):
        super().__init__(
            rule_name="custom_business_rule",
            message=f"Custom business rule violated for entity: {entity_id}",
            context={"entity_id": entity_id, "rule_details": rule_details},
            **kwargs
        )


def example_custom_exception_usage():
    """Example showing custom exception usage."""
    
    entity_id = "entity_123"
    
    # Some business logic check
    if True:  # Replace with actual business logic
        raise CustomBusinessRule(
            entity_id=entity_id,
            rule_details={
                "rule_type": "time_based",
                "violation_time": datetime.utcnow().isoformat(),
                "expected_condition": "operation_allowed_during_business_hours"
            }
        )


# Example 6: Error response handling in FastAPI routes

"""
Example FastAPI route showing how exceptions are automatically handled:

from fastapi import APIRouter, HTTPException
from app.core.exceptions import PartnerNotFound, ValidationError

router = APIRouter()

@router.get("/partners/{partner_id}")
async def get_partner(partner_id: str):
    try:
        # This will automatically be caught by the global error handlers
        partner = get_partner_by_id(partner_id)
        return partner
        
    except PartnerNotFound:
        # This will be automatically converted to a 404 response
        # with structured error data by the domain_exception_handler
        raise
        
    except ValidationError:
        # This will be automatically converted to a 400 response
        # with validation error details
        raise

# The global error handlers will automatically:
# 1. Log the error with proper context
# 2. Return a structured error response
# 3. Include request tracing information
# 4. Hide sensitive internal details for infrastructure errors
"""


if __name__ == "__main__":
    # Example usage
    print("Error handling system examples")
    
    try:
        get_partner_by_id("")
    except ValidationError as e:
        print(f"Caught validation error: {e.message}")
        print(f"Error details: {e.to_dict()}")
    
    try:
        get_partner_by_id("nonexistent")
    except PartnerNotFound as e:
        print(f"Caught not found error: {e.message}")
        print(f"Error details: {e.to_dict()}")