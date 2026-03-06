"""
AstroAI-Core 机器学习模块
"""

from .models.star_classifier import (
    StarClassifier,
    StarClassifierViT,
    CelestialCategory,
    create_model
)

from .data_loader import (
    CelestialDataset,
    HubbleDataset,
    get_transforms,
    create_data_loaders,
    DataAugmenter
)

from .inference import (
    InferenceEngine,
    create_inference_api
)

from .train_classifier import (
    TrainingConfig,
    Trainer
)

__version__ = '1.0.0'
__all__ = [
    # 模型
    'StarClassifier',
    'StarClassifierViT',
    'CelestialCategory',
    'create_model',
    
    # 数据
    'CelestialDataset',
    'HubbleDataset',
    'get_transforms',
    'create_data_loaders',
    'DataAugmenter',
    
    # 推理
    'InferenceEngine',
    'create_inference_api',
    
    # 训练
    'TrainingConfig',
    'Trainer'
]
