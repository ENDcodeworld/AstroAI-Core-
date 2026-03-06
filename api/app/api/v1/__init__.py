"""
API v1 routes
"""

from .exoplanets import router as exoplanets_router
from .images import router as images_router

__all__ = ["exoplanets_router", "images_router"]
