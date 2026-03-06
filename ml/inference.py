"""
推理 API

功能:
- 图像上传接口
- 批量推理接口
- 结果格式化
- 模型加载和预测
"""

import os
import io
import json
import base64
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple
from datetime import datetime

import torch
from torchvision import transforms
from PIL import Image
import numpy as np

from models.star_classifier import StarClassifier, CelestialCategory, create_model
from data_loader import get_transforms


class InferenceEngine:
    """
    推理引擎
    
    提供高效的单张和批量推理能力
    """
    
    def __init__(
        self,
        model_path: str,
        config_path: Optional[str] = None,
        device: str = 'cuda',
        img_size: int = 224
    ):
        """
        初始化推理引擎
        
        Args:
            model_path: 模型权重文件路径
            config_path: 配置文件路径 (可选)
            device: 运行设备
            img_size: 输入图像尺寸
        """
        self.device = device if torch.cuda.is_available() else 'cpu'
        self.img_size = img_size
        
        # 加载模型
        self.model = self._load_model(model_path, config_path)
        self.model.to(self.device)
        self.model.eval()
        
        # 数据变换
        self.transform = get_transforms(img_size, is_training=False, augment=False)
        
        # 类别映射
        self.main_categories = CelestialCategory.get_main_categories()
        self.sub_categories = CelestialCategory.get_subcategories()
        
        print(f"Inference engine initialized on {self.device}")
    
    def _load_model(self, model_path: str, config_path: Optional[str]) -> StarClassifier:
        """加载模型"""
        # 尝试从配置加载
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            model = create_model(
                model_type=config.get('model_type', 'resnet'),
                num_main_classes=config.get('num_main_classes', 3),
                num_sub_classes=config.get('num_sub_classes', 10),
                pretrained=False
            )
        else:
            # 默认配置
            checkpoint = torch.load(model_path, map_location='cpu')
            config = checkpoint.get('config', {})
            
            model = create_model(
                model_type=config.get('model_type', 'resnet'),
                num_main_classes=config.get('num_main_classes', 3),
                num_sub_classes=config.get('num_sub_classes', 10),
                pretrained=False
            )
        
        # 加载权重
        if model_path.endswith('.pth') or model_path.endswith('.pt'):
            checkpoint = torch.load(model_path, map_location='cpu')
            
            if 'model_state_dict' in checkpoint:
                model.load_state_dict(checkpoint['model_state_dict'])
            else:
                model.load_state_dict(checkpoint)
        
        return model
    
    def preprocess_image(self, image: Union[str, Image.Image, np.ndarray]) -> torch.Tensor:
        """
        预处理图像
        
        Args:
            image: 图像路径、PIL 图像或 numpy 数组
            
        Returns:
            预处理后的张量
        """
        # 加载图像
        if isinstance(image, str):
            image = Image.open(image).convert('RGB')
        elif isinstance(image, np.ndarray):
            image = Image.fromarray(image).convert('RGB')
        elif not isinstance(image, Image.Image):
            raise ValueError("Image must be path, PIL Image, or numpy array")
        
        # 应用变换
        tensor = self.transform(image)
        
        # 添加批次维度
        tensor = tensor.unsqueeze(0)
        
        return tensor
    
    def predict(
        self,
        image: Union[str, Image.Image, np.ndarray],
        top_k: int = 3,
        return_features: bool = False
    ) -> Dict:
        """
        单张图像预测
        
        Args:
            image: 输入图像
            top_k: 返回前 K 个预测
            return_features: 是否返回特征
            
        Returns:
            预测结果字典
        """
        # 预处理
        tensor = self.preprocess_image(image)
        tensor = tensor.to(self.device)
        
        # 推理
        with torch.no_grad():
            outputs = self.model(tensor)
            
            # 主类别预测
            main_probs = torch.softmax(outputs['main_logits'], dim=1)
            main_conf, main_pred = torch.topk(main_probs, k=min(top_k, self.model.num_main_classes))
            
            # 细分类预测
            sub_probs = torch.softmax(outputs['sub_logits'], dim=1)
            sub_conf, sub_pred = torch.topk(sub_probs, k=min(top_k, self.model.num_sub_classes))
            
            # 置信度
            confidence = outputs['confidence'].item()
            
            # 构建结果
            result = {
                'timestamp': datetime.now().isoformat(),
                'main_predictions': [
                    {
                        'category': self.main_categories[idx],
                        'category_id': idx,
                        'probability': prob.item(),
                        'confidence': conf.item()
                    }
                    for idx, prob, conf in zip(main_pred[0], main_probs[0, main_pred[0]], main_conf[0])
                ],
                'sub_predictions': [
                    {
                        'category': self.sub_categories[idx],
                        'category_id': idx,
                        'probability': prob.item()
                    }
                    for idx, prob in zip(sub_pred[0], sub_probs[0, sub_pred[0]])
                ][:top_k],
                'overall_confidence': confidence,
                'best_main_category': self.main_categories[main_pred[0, 0].item()],
                'best_sub_category': self.sub_categories[sub_pred[0, 0].item()]
            }
            
            if return_features:
                result['features'] = outputs['features'].cpu().numpy().tolist()
        
        return result
    
    def predict_batch(
        self,
        images: List[Union[str, Image.Image, np.ndarray]],
        batch_size: int = 32,
        top_k: int = 3
    ) -> List[Dict]:
        """
        批量预测
        
        Args:
            images: 图像列表
            batch_size: 批次大小
            top_k: 返回前 K 个预测
            
        Returns:
            预测结果列表
        """
        results = []
        
        # 分批处理
        for i in range(0, len(images), batch_size):
            batch_images = images[i:i + batch_size]
            
            # 预处理批次
            batch_tensors = []
            for img in batch_images:
                tensor = self.preprocess_image(img)
                batch_tensors.append(tensor)
            
            batch_tensor = torch.cat(batch_tensors, dim=0).to(self.device)
            
            # 推理
            with torch.no_grad():
                outputs = self.model(batch_tensor)
                
                main_probs = torch.softmax(outputs['main_logits'], dim=1)
                sub_probs = torch.softmax(outputs['sub_logits'], dim=1)
                confidences = outputs['confidence'].squeeze()
                
                main_conf, main_pred = torch.max(main_probs, dim=1)
                sub_conf, sub_pred = torch.max(sub_probs, dim=1)
                
                # 构建结果
                for j in range(len(batch_images)):
                    result = {
                        'image_index': i + j,
                        'timestamp': datetime.now().isoformat(),
                        'main_category': self.main_categories[main_pred[j].item()],
                        'main_probability': main_probs[j, main_pred[j]].item(),
                        'sub_category': self.sub_categories[sub_pred[j].item()],
                        'sub_probability': sub_probs[j, sub_pred[j]].item(),
                        'overall_confidence': confidences[j].item() if confidences.dim() > 0 else confidences.item(),
                        'all_main_probs': main_probs[j].cpu().numpy().tolist(),
                        'all_sub_probs': sub_probs[j].cpu().numpy().tolist()
                    }
                    results.append(result)
        
        return results
    
    def predict_from_base64(self, base64_string: str, **kwargs) -> Dict:
        """
        从 base64 字符串预测
        
        Args:
            base64_string: base64 编码的图像
            **kwargs: 传递给 predict 的参数
            
        Returns:
            预测结果
        """
        # 解码 base64
        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data)).convert('RGB')
        
        return self.predict(image, **kwargs)
    
    def analyze_image(
        self,
        image: Union[str, Image.Image],
        detailed: bool = True
    ) -> Dict:
        """
        详细图像分析
        
        Args:
            image: 输入图像
            detailed: 是否返回详细分析
            
        Returns:
            分析结果
        """
        # 基础预测
        result = self.predict(image, top_k=5)
        
        if detailed:
            # 添加类别层次信息
            best_main = result['best_main_category']
            best_sub = result['best_sub_category']
            
            # 获取细分类别映射
            sub_for_main = CelestialCategory.get_subcategories_for_main(best_main)
            
            result['analysis'] = {
                'main_category_info': {
                    'name': best_main,
                    'description': self._get_category_description(best_main),
                    'compatible_subcategories': sub_for_main
                },
                'subcategory_consistency': best_sub in sub_for_main,
                'recommendation': self._get_recommendation(result)
            }
        
        return result
    
    def _get_category_description(self, category: str) -> str:
        """获取类别描述"""
        descriptions = {
            'star': '恒星 - 自身发光的天体，通过核聚变产生能量',
            'galaxy': '星系 - 由恒星、气体、尘埃和暗物质组成的巨大系统',
            'nebula': '星云 - 星际空间中的气体和尘埃云',
            'elliptical_galaxy': '椭圆星系 - 呈椭圆形或圆形，主要由老年恒星组成',
            'spiral_galaxy': '螺旋星系 - 具有旋臂结构，包含大量年轻恒星',
            'irregular_galaxy': '不规则星系 - 没有明确形状的星系',
            'emission_nebula': '发射星云 - 被附近恒星电离而发光的星云',
            'reflection_nebula': '反射星云 - 反射附近恒星光线的星云',
            'planetary_nebula': '行星状星云 - 恒星演化末期抛出的外壳',
            'dark_nebula': '暗星云 - 遮挡背景光线的致密尘埃云'
        }
        return descriptions.get(category, '未知类别')
    
    def _get_recommendation(self, result: Dict) -> str:
        """根据预测结果给出建议"""
        confidence = result['overall_confidence']
        main_prob = result['main_predictions'][0]['probability']
        
        if confidence > 0.9 and main_prob > 0.9:
            return "高置信度分类，结果可靠"
        elif confidence > 0.7 and main_prob > 0.7:
            return "中等置信度，建议结合其他信息确认"
        else:
            return "低置信度，建议人工审核或使用更多数据重新训练"
    
    def export_results(self, results: List[Dict], output_path: str, format: str = 'json'):
        """
        导出预测结果
        
        Args:
            results: 预测结果列表
            output_path: 输出路径
            format: 输出格式 ('json' 或 'csv')
        """
        if format == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
        elif format == 'csv':
            import csv
            
            if results:
                keys = results[0].keys()
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=keys)
                    writer.writeheader()
                    writer.writerows(results)
        
        print(f"Results exported to {output_path}")


def create_inference_api(model_path: str, **kwargs) -> InferenceEngine:
    """
    创建推理 API 的工厂函数
    
    Args:
        model_path: 模型路径
        **kwargs: 其他参数
        
    Returns:
        推理引擎实例
    """
    return InferenceEngine(model_path, **kwargs)


# FastAPI 接口示例
def create_fastapi_app(model_path: str):
    """
    创建 FastAPI 应用
    
    用于部署推理服务
    """
    try:
        from fastapi import FastAPI, File, UploadFile, HTTPException
        from fastapi.responses import JSONResponse
        import uvicorn
    except ImportError:
        print("FastAPI not installed. Please install: pip install fastapi uvicorn")
        return None
    
    app = FastAPI(
        title="AstroAI Image Classification API",
        description="天文图像自动分类 API",
        version="1.0.0"
    )
    
    # 初始化推理引擎
    engine = InferenceEngine(model_path)
    
    @app.get("/")
    async def root():
        return {
            "message": "AstroAI Classification API",
            "version": "1.0.0",
            "endpoints": [
                "/classify - 单张图像分类",
                "/classify/batch - 批量分类",
                "/health - 健康检查"
            ]
        }
    
    @app.post("/classify")
    async def classify_image(file: UploadFile = File(...)):
        """
        分类单张图像
        
        - **file**: 上传的图像文件
        """
        try:
            # 读取图像
            contents = await file.read()
            image = Image.open(io.BytesIO(contents)).convert('RGB')
            
            # 预测
            result = engine.predict(image)
            
            return JSONResponse(content=result)
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/classify/batch")
    async def classify_batch(files: List[UploadFile] = File(...)):
        """
        批量分类图像
        
        - **files**: 上传的图像文件列表
        """
        try:
            images = []
            for file in files:
                contents = await file.read()
                image = Image.open(io.BytesIO(contents)).convert('RGB')
                images.append(image)
            
            results = engine.predict_batch(images)
            
            return JSONResponse(content={"results": results, "count": len(results)})
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/health")
    async def health_check():
        """健康检查"""
        return {
            "status": "healthy",
            "device": engine.device,
            "model_type": type(engine.model).__name__
        }
    
    return app


if __name__ == '__main__':
    # 测试推理引擎
    print("Testing inference engine...")
    
    # 创建测试图像
    test_image = Image.new('RGB', (224, 224), color=(100, 100, 100))
    test_image.save('/tmp/test_celestial.jpg')
    
    # 注意：实际使用时需要提供真实的模型路径
    # engine = InferenceEngine(model_path='./checkpoints/best_model.pth')
    # result = engine.predict('/tmp/test_celestial.jpg')
    # print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print("Inference module ready!")
