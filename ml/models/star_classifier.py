"""
StarClassifier - 天文图像分类模型

支持 3 大类分类：恒星、星系、星云
支持细分类：椭圆星系、螺旋星系、发射星云等
基于 ResNet/ViT 架构
"""

import torch
import torch.nn as nn
from torchvision import models
from typing import Dict, List, Tuple, Optional
from enum import Enum


class CelestialCategory(Enum):
    """天体类别枚举"""
    # 主类别
    STAR = "star"  # 恒星
    GALAXY = "galaxy"  # 星系
    NEBULA = "nebula"  # 星云
    
    # 细分类 - 星系
    ELLIPTICAL_GALAXY = "elliptical_galaxy"  # 椭圆星系
    SPIRAL_GALAXY = "spiral_galaxy"  # 螺旋星系
    IRREGULAR_GALAXY = "irregular_galaxy"  # 不规则星系
    
    # 细分类 - 星云
    EMISSION_NEBULA = "emission_nebula"  # 发射星云
    REFLECTION_NEBULA = "reflection_nebula"  # 反射星云
    PLANETARY_NEBULA = "planetary_nebula"  # 行星状星云
    DARK_NEBULA = "dark_nebula"  # 暗星云
    
    @classmethod
    def get_main_categories(cls) -> List[str]:
        """获取主类别列表"""
        return [cls.STAR.value, cls.GALAXY.value, cls.NEBULA.value]
    
    @classmethod
    def get_subcategories(cls) -> List[str]:
        """获取所有细分类别列表"""
        return [e.value for e in cls]
    
    @classmethod
    def get_subcategories_for_main(cls, main_category: str) -> List[str]:
        """获取主类别下的细分类别"""
        mapping = {
            cls.STAR.value: [cls.STAR.value],
            cls.GALAXY.value: [cls.ELLIPTICAL_GALAXY.value, cls.SPIRAL_GALAXY.value, cls.IRREGULAR_GALAXY.value],
            cls.NEBULA.value: [cls.EMISSION_NEBULA.value, cls.REFLECTION_NEBULA.value, 
                              cls.PLANETARY_NEBULA.value, cls.DARK_NEBULA.value]
        }
        return mapping.get(main_category, [])


class StarClassifier(nn.Module):
    """
    天文图像分类器
    
    特性:
    - 基于 ResNet50 的迁移学习
    - 双输出头：主类别 + 细分类
    - 置信度评分
    - 支持多标签分类
    """
    
    def __init__(
        self,
        num_main_classes: int = 3,
        num_sub_classes: int = 10,
        pretrained: bool = True,
        dropout_rate: float = 0.3,
        use_attention: bool = True
    ):
        super(StarClassifier, self).__init__()
        
        self.num_main_classes = num_main_classes
        self.num_sub_classes = num_sub_classes
        self.use_attention = use_attention
        
        # 加载预训练的 ResNet50 作为骨干网络
        backbone = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2 if pretrained else None)
        
        # 移除原始全连接层
        self.features = nn.Sequential(*list(backbone.children())[:-1])
        self.feature_dim = backbone.fc.in_features
        
        # 注意力机制 (可选)
        if self.use_attention:
            self.attention = nn.Sequential(
                nn.Linear(self.feature_dim, self.feature_dim // 4),
                nn.ReLU(),
                nn.Linear(self.feature_dim // 4, self.feature_dim),
                nn.Sigmoid()
            )
        
        # 主类别分类头
        self.main_classifier = nn.Sequential(
            nn.Dropout(dropout_rate),
            nn.Linear(self.feature_dim, 256),
            nn.ReLU(),
            nn.Dropout(dropout_rate / 2),
            nn.Linear(256, num_main_classes)
        )
        
        # 细分类分类头
        self.sub_classifier = nn.Sequential(
            nn.Dropout(dropout_rate),
            nn.Linear(self.feature_dim, 512),
            nn.ReLU(),
            nn.Dropout(dropout_rate / 2),
            nn.Linear(512, num_sub_classes)
        )
        
        # 置信度估计头
        self.confidence_head = nn.Sequential(
            nn.Linear(self.feature_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        前向传播
        
        Args:
            x: 输入图像张量 [B, C, H, W]
            
        Returns:
            包含主类别、细分类和置信度的字典
        """
        # 提取特征
        features = self.features(x)
        features = features.view(features.size(0), -1)  # [B, feature_dim]
        
        # 应用注意力
        if self.use_attention:
            attention_weights = self.attention(features)
            features = features * attention_weights
        
        # 分类
        main_logits = self.main_classifier(features)
        sub_logits = self.sub_classifier(features)
        confidence = self.confidence_head(features)
        
        return {
            'main_logits': main_logits,
            'sub_logits': sub_logits,
            'confidence': confidence,
            'features': features
        }
    
    def predict(
        self,
        x: torch.Tensor,
        threshold: float = 0.5
    ) -> Dict[str, any]:
        """
        预测接口
        
        Args:
            x: 输入图像张量
            threshold: 置信度阈值
            
        Returns:
            预测结果字典
        """
        self.eval()
        with torch.no_grad():
            outputs = self.forward(x)
            
            # 主类别预测
            main_probs = torch.softmax(outputs['main_logits'], dim=1)
            main_conf, main_pred = torch.max(main_probs, dim=1)
            
            # 细分类预测
            sub_probs = torch.softmax(outputs['sub_logits'], dim=1)
            sub_conf, sub_pred = torch.max(sub_probs, dim=1)
            
            # 整体置信度
            overall_confidence = outputs['confidence'].squeeze()
            
            return {
                'main_category_id': main_pred.item(),
                'main_category_prob': main_conf.item(),
                'sub_category_id': sub_pred.item(),
                'sub_category_prob': sub_conf.item(),
                'overall_confidence': overall_confidence.item(),
                'main_probs': main_probs.cpu().numpy(),
                'sub_probs': sub_probs.cpu().numpy()
            }
    
    def get_feature_extractor(self) -> nn.Module:
        """获取特征提取器用于迁移学习"""
        return self.features


class StarClassifierViT(StarClassifier):
    """
    基于 Vision Transformer 的天文图像分类器
    
    适用于需要捕捉全局特征的场景
    """
    
    def __init__(
        self,
        num_main_classes: int = 3,
        num_sub_classes: int = 10,
        pretrained: bool = True,
        img_size: int = 224,
        patch_size: int = 16,
        embed_dim: int = 768,
        depth: int = 12,
        num_heads: int = 12,
        dropout_rate: float = 0.1
    ):
        nn.Module.__init__(self)
        
        self.num_main_classes = num_main_classes
        self.num_sub_classes = num_sub_classes
        
        # 使用预训练的 ViT
        if pretrained:
            self.vit = models.vit_b_16(weights=models.ViT_B_16_Weights.IMAGENET1K_V1)
            self.feature_dim = 768
        else:
            # 简化的 ViT 实现
            self.vit = self._create_vit(img_size, patch_size, embed_dim, depth, num_heads)
            self.feature_dim = embed_dim
        
        # 分类头
        self.main_classifier = nn.Sequential(
            nn.Dropout(dropout_rate),
            nn.Linear(self.feature_dim, num_main_classes)
        )
        
        self.sub_classifier = nn.Sequential(
            nn.Dropout(dropout_rate),
            nn.Linear(self.feature_dim, 512),
            nn.ReLU(),
            nn.Dropout(dropout_rate / 2),
            nn.Linear(512, num_sub_classes)
        )
        
        self.confidence_head = nn.Sequential(
            nn.Linear(self.feature_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 1),
            nn.Sigmoid()
        )
    
    def _create_vit(self, img_size, patch_size, embed_dim, depth, num_heads):
        """创建简化的 ViT 模型"""
        # 这里使用 torchvision 的 ViT 作为基础
        return models.vit_b_16(weights=None)
    
    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        """前向传播"""
        # ViT 特征提取
        features = self.vit(x)
        
        # 如果是元组，取第一个元素 (class token)
        if isinstance(features, tuple):
            features = features[0]
        
        # 确保是 2D 特征
        if len(features.shape) == 3:
            features = features[:, 0]  # 取 class token
        
        main_logits = self.main_classifier(features)
        sub_logits = self.sub_classifier(features)
        confidence = self.confidence_head(features)
        
        return {
            'main_logits': main_logits,
            'sub_logits': sub_logits,
            'confidence': confidence,
            'features': features
        }


def create_model(
    model_type: str = 'resnet',
    num_main_classes: int = 3,
    num_sub_classes: int = 10,
    pretrained: bool = True,
    **kwargs
) -> StarClassifier:
    """
    创建模型的工厂函数
    
    Args:
        model_type: 模型类型 ('resnet' 或 'vit')
        num_main_classes: 主类别数量
        num_sub_classes: 细分类数量
        pretrained: 是否使用预训练权重
        
    Returns:
        模型实例
    """
    if model_type.lower() == 'resnet':
        return StarClassifier(
            num_main_classes=num_main_classes,
            num_sub_classes=num_sub_classes,
            pretrained=pretrained,
            **kwargs
        )
    elif model_type.lower() == 'vit':
        return StarClassifierViT(
            num_main_classes=num_main_classes,
            num_sub_classes=num_sub_classes,
            pretrained=pretrained,
            **kwargs
        )
    else:
        raise ValueError(f"Unknown model type: {model_type}")


if __name__ == '__main__':
    # 测试模型
    model = create_model('resnet')
    dummy_input = torch.randn(2, 3, 224, 224)
    output = model(dummy_input)
    
    print("Model output keys:", output.keys())
    print("Main logits shape:", output['main_logits'].shape)
    print("Sub logits shape:", output['sub_logits'].shape)
    print("Confidence shape:", output['confidence'].shape)
    
    # 测试预测
    pred = model.predict(dummy_input)
    print("\nPrediction result:")
    for k, v in pred.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.4f}")
        else:
            print(f"  {k}: {v}")
