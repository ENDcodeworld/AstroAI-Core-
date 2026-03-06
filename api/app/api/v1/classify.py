"""
天文图像分类 API 端点

提供 RESTful API 用于天文图像分类
"""

import io
import os
import sys
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / 'ml'))

from fastapi import APIRouter, File, UploadFile, HTTPException, Query, Body
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
import numpy as np

try:
    from PIL import Image
    import torch
except ImportError as e:
    raise ImportError(f"Required package not installed: {e}. Please install: pip install torch torchvision pillow")

# 导入推理引擎
try:
    from ml.inference import InferenceEngine
    INFERENCE_AVAILABLE = True
except ImportError:
    INFERENCE_AVAILABLE = False
    InferenceEngine = None

router = APIRouter(
    prefix="/classify",
    tags=["classification"],
    responses={404: {"description": "Not found"}}
)

# 全局推理引擎实例
_inference_engine = None


def get_inference_engine() -> Optional[InferenceEngine]:
    """获取推理引擎实例"""
    global _inference_engine
    
    if not INFERENCE_AVAILABLE:
        return None
    
    if _inference_engine is None:
        # 从环境变量或默认路径加载模型
        model_path = os.getenv(
            'ASTROAI_MODEL_PATH',
            str(project_root / 'ml' / 'checkpoints' / 'best_model.pth')
        )
        
        if os.path.exists(model_path):
            _inference_engine = InferenceEngine(model_path=model_path)
        else:
            print(f"Warning: Model not found at {model_path}")
    
    return _inference_engine


# ==================== 数据模型 ====================

class ClassificationResult(BaseModel):
    """分类结果"""
    timestamp: str
    main_category: str = Field(..., description="主类别")
    main_probability: float = Field(..., description="主类别概率", ge=0, le=1)
    sub_category: str = Field(..., description="细分类别")
    sub_probability: float = Field(..., description="细分类别概率", ge=0, le=1)
    overall_confidence: float = Field(..., description="整体置信度", ge=0, le=1)


class DetailedPrediction(BaseModel):
    """详细预测结果"""
    timestamp: str
    best_main_category: str
    best_sub_category: str
    overall_confidence: float
    main_predictions: List[Dict]
    sub_predictions: List[Dict]
    analysis: Optional[Dict] = None


class BatchClassificationResponse(BaseModel):
    """批量分类响应"""
    results: List[ClassificationResult]
    count: int
    processing_time_ms: float


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    device: Optional[str]
    model_loaded: bool
    inference_available: bool


# ==================== API 端点 ====================

@router.get("/", response_model=Dict)
async def classify_root():
    """
    API 根路径
    
    返回 API 信息和可用端点
    """
    return {
        "service": "AstroAI Classification API",
        "version": "1.0.0",
        "description": "天文图像自动分类服务",
        "endpoints": {
            "POST /classify/image": "分类单张图像",
            "POST /classify/batch": "批量分类图像",
            "POST /classify/base64": "从 base64 分类",
            "GET /classify/categories": "获取支持的类别列表",
            "GET /health": "健康检查"
        }
    }


@router.post("/image", response_model=DetailedPrediction)
async def classify_image(
    file: UploadFile = File(..., description="上传的天文图像文件"),
    top_k: int = Query(3, ge=1, le=10, description="返回前 K 个预测结果"),
    detailed: bool = Query(True, description="是否返回详细分析")
):
    """
    分类单张天文图像
    
    **支持的图像格式**: JPEG, PNG, WebP
    
    **返回**:
    - 主类别预测（恒星/星系/星云）
    - 细分类别预测（椭圆星系、螺旋星系等）
    - 置信度评分
    - 详细分析（可选）
    """
    engine = get_inference_engine()
    
    if not engine:
        raise HTTPException(
            status_code=503,
            detail="Inference engine not available. Please check model path."
        )
    
    try:
        # 验证文件类型
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")
        
        # 读取并处理图像
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert('RGB')
        
        # 检查图像尺寸
        if min(image.size) < 64:
            raise HTTPException(
                status_code=400,
                detail="Image too small. Minimum dimension is 64 pixels."
            )
        
        # 执行预测
        if detailed:
            result = engine.analyze_image(image, detailed=True)
        else:
            result = engine.predict(image, top_k=top_k)
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")


@router.post("/batch", response_model=BatchClassificationResponse)
async def classify_batch(
    files: List[UploadFile] = File(..., description="上传的图像文件列表"),
    batch_size: int = Query(32, ge=1, le=128, description="批处理大小")
):
    """
    批量分类多张天文图像
    
    **限制**:
    - 最多 100 张图像 per request
    - 每张图像最大 10MB
    
    **返回**:
    - 所有图像的分类结果
    - 处理时间统计
    """
    engine = get_inference_engine()
    
    if not engine:
        raise HTTPException(
            status_code=503,
            detail="Inference engine not available."
        )
    
    if len(files) > 100:
        raise HTTPException(
            status_code=400,
            detail="Maximum 100 images per request."
        )
    
    start_time = datetime.now()
    results = []
    
    try:
        images = []
        for file in files:
            if not file.content_type or not file.content_type.startswith('image/'):
                continue
            
            contents = await file.read()
            image = Image.open(io.BytesIO(contents)).convert('RGB')
            images.append(image)
        
        if not images:
            raise HTTPException(status_code=400, detail="No valid images found.")
        
        # 批量预测
        predictions = engine.predict_batch(images, batch_size=batch_size)
        
        # 格式化结果
        for pred in predictions:
            results.append(ClassificationResult(
                timestamp=pred['timestamp'],
                main_category=pred['main_category'],
                main_probability=pred['main_probability'],
                sub_category=pred['sub_category'],
                sub_probability=pred['sub_probability'],
                overall_confidence=pred['overall_confidence']
            ))
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return BatchClassificationResponse(
            results=results,
            count=len(results),
            processing_time_ms=processing_time
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch classification failed: {str(e)}")


@router.post("/base64", response_model=DetailedPrediction)
async def classify_base64(
    payload: Dict = Body(..., description="包含 base64 图像的 JSON"),
    top_k: int = Query(3, ge=1, le=10)
):
    """
    从 base64 编码的图像进行分类
    
    **请求格式**:
    ```json
    {
        "image": "base64_encoded_string",
        "filename": "optional_filename.jpg"
    }
    ```
    """
    engine = get_inference_engine()
    
    if not engine:
        raise HTTPException(status_code=503, detail="Inference engine not available.")
    
    try:
        if 'image' not in payload:
            raise HTTPException(status_code=400, detail="Missing 'image' field in request.")
        
        base64_string = payload['image']
        
        # 移除可能的前缀
        if base64_string.startswith('data:image'):
            base64_string = base64_string.split(',')[1]
        
        result = engine.predict_from_base64(base64_string, top_k=top_k)
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")


@router.get("/categories", response_model=Dict)
async def get_categories():
    """
    获取支持的天体类别列表
    
    **返回**:
    - 主类别（3 类）
    - 细分类别（10 类）
    - 类别层次关系
    """
    from ml.models.star_classifier import CelestialCategory
    
    return {
        "main_categories": CelestialCategory.get_main_categories(),
        "sub_categories": CelestialCategory.get_subcategories(),
        "category_hierarchy": {
            "star": CelestialCategory.get_subcategories_for_main("star"),
            "galaxy": CelestialCategory.get_subcategories_for_main("galaxy"),
            "nebula": CelestialCategory.get_subcategories_for_main("nebula")
        },
        "total_classes": len(CelestialCategory.get_subcategories())
    }


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    健康检查端点
    
    检查服务状态、模型加载情况和设备信息
    """
    engine = get_inference_engine()
    
    return HealthResponse(
        status="healthy" if engine else "degraded",
        device=engine.device if engine else None,
        model_loaded=engine is not None,
        inference_available=INFERENCE_AVAILABLE
    )


@router.get("/demo")
async def demo_page():
    """
    返回简单的 HTML 演示页面
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AstroAI - 天文图像分类</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; }
            .upload-area { border: 2px dashed #ccc; padding: 40px; text-align: center; margin: 20px 0; }
            .result { background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 5px; }
            button { background: #007bff; color: white; border: none; padding: 10px 20px; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>🔬 AstroAI 天文图像分类</h1>
        <p>上传天文图像，自动识别恒星、星系、星云等天体</p>
        
        <div class="upload-area">
            <input type="file" id="imageInput" accept="image/*">
            <br><br>
            <button onclick="classifyImage()">开始分类</button>
        </div>
        
        <div id="result" class="result" style="display:none;"></div>
        
        <script>
            async function classifyImage() {
                const fileInput = document.getElementById('imageInput');
                const file = fileInput.files[0];
                
                if (!file) {
                    alert('请选择图像文件');
                    return;
                }
                
                const formData = new FormData();
                formData.append('file', file);
                
                try {
                    const response = await fetch('/classify/image', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    const resultDiv = document.getElementById('result');
                    resultDiv.style.display = 'block';
                    resultDiv.innerHTML = `
                        <h3>分类结果</h3>
                        <p><strong>主类别:</strong> ${result.best_main_category}</p>
                        <p><strong>细分类别:</strong> ${result.best_sub_category}</p>
                        <p><strong>置信度:</strong> ${(result.overall_confidence * 100).toFixed(2)}%</p>
                        <pre>${JSON.stringify(result, null, 2)}</pre>
                    `;
                } catch (error) {
                    alert('分类失败：' + error.message);
                }
            }
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)


# 需要导入 HTMLResponse
try:
    from fastapi.responses import HTMLResponse
except ImportError:
    HTMLResponse = None


if __name__ == '__main__':
    # 测试运行
    import uvicorn
    
    print("Starting AstroAI Classification API...")
    uvicorn.run(
        "classify:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
