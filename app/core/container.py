"""Dependency Injection Container

Provides singleton and transient service registration with automatic dependency resolution.
Supports easy testing through mock substitution and lazy initialization of services.
"""

import inspect
from functools import wraps
from typing import Any, Callable, Optional, TypeVar

T = TypeVar("T")


class ServiceLifetime:
    """Service lifetime constants"""

    SINGLETON = "singleton"
    TRANSIENT = "transient"


class ServiceDescriptor:
    """Describes how a service should be created and managed"""

    def __init__(
        self,
        interface: type,
        implementation: Optional[type] = None,
        factory: Optional[Callable] = None,
        lifetime: str = ServiceLifetime.TRANSIENT,
    ):
        self.interface = interface
        self.implementation = implementation
        self.factory = factory
        self.lifetime = lifetime

        if not implementation and not factory:
            raise ValueError("Either implementation or factory must be provided")


class Container:
    """Simple dependency injection container with support for:
    - Singleton and transient service registration
    - Automatic dependency resolution
    - Easy testing through mock substitution
    - Lazy initialization of services
    """

    def __init__(self):
        self._services: dict[type, ServiceDescriptor] = {}
        self._singletons: dict[type, Any] = {}

    def register_singleton(
        self, interface: type[T], implementation: type[T]
    ) -> "Container":
        """Register a service as singleton (one instance for the lifetime of the container)

        Args:
            interface: The interface/abstract class
            implementation: The concrete implementation class

        Returns:
            Self for method chaining
        """
        self._services[interface] = ServiceDescriptor(
            interface=interface,
            implementation=implementation,
            lifetime=ServiceLifetime.SINGLETON,
        )
        return self

    def register_transient(
        self, interface: type[T], implementation: type[T]
    ) -> "Container":
        """Register a service as transient (new instance every time)

        Args:
            interface: The interface/abstract class
            implementation: The concrete implementation class

        Returns:
            Self for method chaining
        """
        self._services[interface] = ServiceDescriptor(
            interface=interface,
            implementation=implementation,
            lifetime=ServiceLifetime.TRANSIENT,
        )
        return self

    def register_factory(
        self,
        interface: type[T],
        factory: Callable[[], T],
        lifetime: str = ServiceLifetime.TRANSIENT,
    ) -> "Container":
        """Register a service using a factory function

        Args:
            interface: The interface/abstract class
            factory: Factory function that creates the service instance
            lifetime: Service lifetime (singleton or transient)

        Returns:
            Self for method chaining
        """
        self._services[interface] = ServiceDescriptor(
            interface=interface, factory=factory, lifetime=lifetime
        )
        return self

    def register_instance(self, interface: type[T], instance: T) -> "Container":
        """Register a specific instance as singleton

        Args:
            interface: The interface/abstract class
            instance: The instance to register

        Returns:
            Self for method chaining
        """
        self._services[interface] = ServiceDescriptor(
            interface=interface,
            factory=lambda: instance,
            lifetime=ServiceLifetime.SINGLETON,
        )
        self._singletons[interface] = instance
        return self

    def get(self, interface: type[T]) -> T:
        """Get a service instance by interface

        Args:
            interface: The interface/abstract class to resolve

        Returns:
            Service instance

        Raises:
            ValueError: If service is not registered
        """
        if interface not in self._services:
            raise ValueError(f"Service {interface.__name__} is not registered")

        descriptor = self._services[interface]

        # Return singleton if already created
        if (
            descriptor.lifetime == ServiceLifetime.SINGLETON
            and interface in self._singletons
        ):
            return self._singletons[interface]

        # Create new instance
        instance = self._create_instance(descriptor)

        # Store singleton
        if descriptor.lifetime == ServiceLifetime.SINGLETON:
            self._singletons[interface] = instance

        return instance

    def _create_instance(self, descriptor: ServiceDescriptor) -> Any:
        """Create a new service instance"""
        if descriptor.factory:
            return descriptor.factory()

        if descriptor.implementation:
            return self._create_with_dependencies(descriptor.implementation)

        raise ValueError("No factory or implementation provided")

    def _create_with_dependencies(self, implementation: type) -> Any:
        """Create instance with automatic dependency injection"""
        # Get constructor signature
        signature = inspect.signature(implementation.__init__)
        parameters = signature.parameters

        # Skip 'self' parameter
        param_names = [name for name in parameters.keys() if name != "self"]

        # Resolve dependencies
        dependencies = {}
        for param_name in param_names:
            param = parameters[param_name]
            param_type = param.annotation

            if param_type == inspect.Parameter.empty:
                raise ValueError(
                    f"Parameter {param_name} in {implementation.__name__} has no type annotation"
                )

            # Resolve dependency
            dependencies[param_name] = self.get(param_type)

        return implementation(**dependencies)

    def is_registered(self, interface: type) -> bool:
        """Check if a service is registered"""
        return interface in self._services

    def clear(self) -> None:
        """Clear all registrations and singletons"""
        self._services.clear()
        self._singletons.clear()


# Global container instance
_container: Optional[Container] = None


def get_container() -> Container:
    """Get the global container instance"""
    global _container
    if _container is None:
        _container = Container()
    return _container


def set_container(container: Container) -> None:
    """Set the global container instance (useful for testing)"""
    global _container
    _container = container


def inject(interface: type[T]) -> T:
    """Decorator for dependency injection in functions

    Usage:
        @inject
        def my_function(service: IMyService) -> str:
            return service.do_something()
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature
            signature = inspect.signature(func)

            # Inject dependencies for parameters not provided
            for param_name, param in signature.parameters.items():
                if (
                    param_name not in kwargs
                    and param.annotation != inspect.Parameter.empty
                ):
                    container = get_container()
                    if container.is_registered(param.annotation):
                        kwargs[param_name] = container.get(param.annotation)

            return func(*args, **kwargs)

        return wrapper

    return decorator
