"""
模型模块
"""

from .star_classifier import (
    StarClassifier,
    StarClassifierViT,
    CelestialCategory,
    create_model
)

__all__ = [
    'StarClassifier',
    'StarClassifierViT',
    'CelestialCategory',
    'create_model'
]
