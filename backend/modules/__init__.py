from .auth_routes import auth_router
from .provider_routes import provider_router
from .generation_routes import generation_router

__all__ = ['auth_router', 'provider_router', 'generation_router']