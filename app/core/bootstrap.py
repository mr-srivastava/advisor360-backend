"""Application Bootstrap

Handles dependency registration and application initialization.
Sets up the dependency injection container with all required services and repositories.
"""

import logging

from supabase import Client, create_client

# Repository interfaces
from ..repositories.interfaces.commission_repository import ICommissionRepository
from ..repositories.interfaces.partner_repository import IPartnerRepository

# Repository implementations
from ..repositories.supabase.commission_repository import CommissionRepository
from ..repositories.supabase.partner_repository import PartnerRepository

# Service implementations
from ..services.commissions import CommissionService
from ..services.dashboard import DashboardService

# Service interfaces
from ..services.interfaces.commission_service import ICommissionService
from ..services.interfaces.dashboard_service import IDashboardService
from ..services.interfaces.partner_service import IPartnerService
from ..services.partners import PartnerService
from .config.app_config import get_config
from .container import Container, get_container

logger = logging.getLogger(__name__)


def create_supabase_client() -> Client:
    """Create and configure Supabase client.

    Returns:
        Client: Configured Supabase client
    """
    config = get_config()

    logger.info("Creating Supabase client")
    client = create_client(
        supabase_url=config.database_url, supabase_key=config.database_key
    )

    logger.info("Supabase client created successfully")
    return client


def register_dependencies(container: Container) -> None:
    """Register all application dependencies in the DI container.

    Args:
        container: The dependency injection container
    """
    logger.info("Starting dependency registration")

    # Register Supabase client as singleton
    supabase_client = create_supabase_client()
    container.register_instance(Client, supabase_client)

    # Register repositories as singletons
    container.register_singleton(ICommissionRepository, CommissionRepository)
    container.register_singleton(IPartnerRepository, PartnerRepository)

    # Register services as singletons
    container.register_singleton(ICommissionService, CommissionService)
    container.register_singleton(IPartnerService, PartnerService)
    container.register_singleton(IDashboardService, DashboardService)

    logger.info("Dependency registration completed successfully")


def bootstrap_application() -> Container:
    """Bootstrap the application by setting up dependencies.

    Returns:
        Container: The configured dependency injection container
    """
    logger.info("Bootstrapping application")

    # Get or create container
    container = get_container()

    # Register all dependencies
    register_dependencies(container)

    logger.info("Application bootstrap completed")
    return container


def validate_dependencies(container: Container) -> None:
    """Validate that all required dependencies are properly registered.

    Args:
        container: The dependency injection container

    Raises:
        ValueError: If required dependencies are missing
    """
    logger.info("Validating dependencies")

    required_services = [ICommissionService, IPartnerService, IDashboardService]

    required_repositories = [ICommissionRepository, IPartnerRepository]

    # Check services
    for service_interface in required_services:
        if not container.is_registered(service_interface):
            raise ValueError(
                f"Required service {service_interface.__name__} is not registered"
            )

        # Try to resolve the service
        try:
            service = container.get(service_interface)
            logger.debug(
                f"Successfully resolved {service_interface.__name__}: {type(service).__name__}"
            )
        except Exception as e:
            raise ValueError(
                f"Failed to resolve {service_interface.__name__}: {str(e)}"
            )

    # Check repositories
    for repo_interface in required_repositories:
        if not container.is_registered(repo_interface):
            raise ValueError(
                f"Required repository {repo_interface.__name__} is not registered"
            )

        # Try to resolve the repository
        try:
            repo = container.get(repo_interface)
            logger.debug(
                f"Successfully resolved {repo_interface.__name__}: {type(repo).__name__}"
            )
        except Exception as e:
            raise ValueError(f"Failed to resolve {repo_interface.__name__}: {str(e)}")

    logger.info("All dependencies validated successfully")


def setup_application() -> Container:
    """Complete application setup including bootstrap and validation.

    Returns:
        Container: The configured and validated dependency injection container
    """
    try:
        # Bootstrap the application
        container = bootstrap_application()

        # Validate dependencies
        validate_dependencies(container)

        logger.info("Application setup completed successfully")
        return container

    except Exception as e:
        logger.error(f"Application setup failed: {str(e)}")
        raise
