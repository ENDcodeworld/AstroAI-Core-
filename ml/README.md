# AstroAI-Core 机器学习模块

天文图像自动分类系统 - 使用深度学习技术识别恒星、星系、星云等天体

## 📋 目录

- [功能特性](#功能特性)
- [快速开始](#快速开始)
- [模型架构](#模型架构)
- [数据准备](#数据准备)
- [训练指南](#训练指南)
- [推理使用](#推理使用)
- [API 文档](#api 文档)
- [项目结构](#项目结构)

## ✨ 功能特性

### 核心能力

- **三大主类别分类**: 恒星 (Star)、星系 (Galaxy)、星云 (Nebula)
- **细分类识别**:
  - 星系：椭圆星系、螺旋星系、不规则星系
  - 星云：发射星云、反射星云、行星状星云、暗星云
- **置信度评分**: 为每个预测提供可靠的置信度评估
- **批量推理**: 支持高效批量处理

### 技术特性

- 基于 ResNet50 和 Vision Transformer 的先进架构
- 迁移学习加速训练
- 混合精度训练支持
- 自动数据增强
- 早停和学习率调度
- 完整的训练可视化和日志

## 🚀 快速开始

### 安装依赖

```bash
pip install torch torchvision torchaudio
pip install pillow numpy tqdm matplotlib
pip install fastapi uvicorn python-multipart  # API 服务
```

### 基础使用

```python
from ml.inference import InferenceEngine

# 加载模型
engine = InferenceEngine(model_path='./ml/checkpoints/best_model.pth')

# 单张图像预测
result = engine.predict('path/to/image.jpg')
print(f"类别：{result['best_main_category']}")
print(f"置信度：{result['overall_confidence']:.2%}")

# 批量预测
images = ['img1.jpg', 'img2.jpg', 'img3.jpg']
results = engine.predict_batch(images)
```

## 🏗️ 模型架构

### StarClassifier (基于 ResNet)

```
输入图像 (3×224×224)
    ↓
ResNet50 骨干网络
    ↓
注意力机制 (可选)
    ↓
┌───────────────┬───────────────┬─────────────┐
│  主分类头     │  细分类头     │  置信度头   │
│  (3 类)       │  (10 类)      │  (0-1)      │
└───────────────┴───────────────┴─────────────┘
```

### StarClassifierViT (基于 Vision Transformer)

适用于需要捕捉全局特征的场景，对大规模结构（如星系形态）有更好的识别能力。

### 类别体系

```
天体
├── 恒星 (Star)
├── 星系 (Galaxy)
│   ├── 椭圆星系
│   ├── 螺旋星系
│   └── 不规则星系
└── 星云 (Nebula)
    ├── 发射星云
    ├── 反射星云
    ├── 行星状星云
    └── 暗星云
```

## 📊 数据准备

### 目录结构

```
data/
├── star/
│   ├── image1.jpg
│   └── image2.jpg
├── galaxy/
│   ├── elliptical/
│   ├── spiral/
│   └── irregular/
└── nebula/
    ├── emission/
    ├── reflection/
    ├── planetary/
    └── dark/
```

### 使用 Hubble 数据集

1. 从 [Hubble Legacy Archive](https://hla.stsci.edu/) 下载图像
2. 按类别组织到对应目录
3. 运行数据增强:

```python
from ml.data_loader import DataAugmenter

DataAugmenter.create_augmented_dataset(
    input_dir='./data/original',
    output_dir='./data/augmented',
    augmentation_factor=5
)
```

### 数据格式要求

- **格式**: JPEG, PNG, WebP
- **最小尺寸**: 128×128 像素
- **推荐尺寸**: 224×224 或更高
- **色彩空间**: RGB

## 🎯 训练指南

### 基础训练

```python
from ml.train_classifier import TrainingConfig, Trainer
from ml.data_loader import create_data_loaders

# 配置
config = TrainingConfig(
    data_dir='./data/celestial',
    batch_size=32,
    epochs=50,
    learning_rate=1e-3,
    model_type='resnet'
)

# 创建数据加载器
train_loader, val_loader, test_loader = create_data_loaders(
    data_dir=config.data_dir,
    batch_size=config.batch_size
)

# 创建训练器
trainer = Trainer(config)

# 开始训练
history = trainer.train(train_loader, val_loader)

# 保存训练曲线
trainer.plot_history(save_path='./logs/training_curves.png')
```

### 高级配置

```python
config = TrainingConfig(
    # 模型配置
    model_type='vit',  # 或 'resnet'
    pretrained=True,
    
    # 训练配置
    epochs=100,
    batch_size=64,
    learning_rate=5e-4,
    optimizer='adamw',
    scheduler='cosine',
    
    # 正则化
    dropout_rate=0.3,
    label_smoothing=0.1,
    
    # 早停
    early_stopping=True,
    patience=10,
    
    # 混合精度训练
    mixed_precision=True
)
```

### 训练监控

训练过程中会自动保存:

- **检查点**: `./checkpoints/checkpoint_epoch_X.pth`
- **最佳模型**: `./checkpoints/best_model.pth`
- **训练历史**: `./logs/training_history.json`
- **训练曲线**: `./logs/training_curves.png`

## 🔮 推理使用

### 单张图像分类

```python
from ml.inference import InferenceEngine

engine = InferenceEngine(model_path='./checkpoints/best_model.pth')

# 从文件路径
result = engine.predict('galaxy_image.jpg')

# 从 PIL Image
from PIL import Image
img = Image.open('image.jpg')
result = engine.predict(img)

# 从 numpy 数组
import numpy as np
img_array = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
result = engine.predict(img_array)

print(result)
```

### 详细分析

```python
result = engine.analyze_image('image.jpg', detailed=True)

print(f"主类别：{result['best_main_category']}")
print(f"细分类：{result['best_sub_category']}")
print(f"置信度：{result['overall_confidence']:.2%}")
print(f"类别描述：{result['analysis']['main_category_info']['description']}")
print(f"建议：{result['analysis']['recommendation']}")
```

### 批量推理

```python
image_paths = ['img1.jpg', 'img2.jpg', 'img3.jpg', ...]
results = engine.predict_batch(image_paths, batch_size=32)

# 导出结果
engine.export_results(results, 'predictions.json', format='json')
engine.export_results(results, 'predictions.csv', format='csv')
```

### Base64 图像

```python
import base64

with open('image.jpg', 'rb') as f:
    base64_str = base64.b64encode(f.read()).decode()

result = engine.predict_from_base64(base64_str)
```

## 🌐 API 文档

### 启动服务

```bash
cd api
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### API 端点

#### 1. 单张图像分类

```bash
curl -X POST "http://localhost:8000/classify/image" \
  -F "file=@galaxy.jpg" \
  -F "top_k=3" \
  -F "detailed=true"
```

**响应示例**:
```json
{
  "timestamp": "2024-01-01T12:00:00",
  "best_main_category": "galaxy",
  "best_sub_category": "spiral_galaxy",
  "overall_confidence": 0.95,
  "main_predictions": [
    {"category": "galaxy", "probability": 0.95},
    {"category": "nebula", "probability": 0.04},
    {"category": "star", "probability": 0.01}
  ],
  "sub_predictions": [...],
  "analysis": {
    "main_category_info": {...},
    "recommendation": "高置信度分类，结果可靠"
  }
}
```

#### 2. 批量分类

```bash
curl -X POST "http://localhost:8000/classify/batch" \
  -F "files=@img1.jpg" \
  -F "files=@img2.jpg" \
  -F "files=@img3.jpg"
```

#### 3. Base64 分类

```bash
curl -X POST "http://localhost:8000/classify/base64" \
  -H "Content-Type: application/json" \
  -d '{"image": "base64_encoded_string"}'
```

#### 4. 获取类别列表

```bash
curl "http://localhost:8000/classify/categories"
```

#### 5. 健康检查

```bash
curl "http://localhost:8000/classify/health"
```

### Python 客户端

```python
import requests

# 单张分类
with open('image.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/classify/image',
        files={'file': f}
    )
    result = response.json()

# 批量分类
files = [
    ('files', open('img1.jpg', 'rb')),
    ('files', open('img2.jpg', 'rb'))
]
response = requests.post(
    'http://localhost:8000/classify/batch',
    files=files
)
```

## 📁 项目结构

```
AstroAI-Core/
├── ml/
│   ├── models/
│   │   └── star_classifier.py    # 模型架构定义
│   ├── data_loader.py            # 数据加载和增强
│   ├── train_classifier.py       # 训练管道
│   ├── inference.py              # 推理引擎
│   ├── checkpoints/              # 模型检查点
│   ├── logs/                     # 训练日志
│   └── README.md                 # 本文档
├── api/
│   └── app/
│       └── api/
│           └── v1/
│               └── classify.py   # API 端点
├── tests/
│   └── test_classifier.py        # 单元测试
├── data/                         # 数据集
└── requirements.txt              # 依赖
```

## 🧪 测试

运行测试套件:

```bash
cd tests
python test_classifier.py
```

或单独运行:

```bash
python -m unittest tests.test_classifier.TestStarClassifier
```

## 📝 最佳实践

### 数据准备

1. **数据质量**: 确保图像清晰，标签准确
2. **类别平衡**: 各类别样本数量尽量均衡
3. **数据增强**: 使用旋转、翻转等增强技术扩充数据
4. **验证集**: 保留 15-20% 数据用于验证

### 模型训练

1. **预训练**: 始终使用 ImageNet 预训练权重
2. **学习率**: 从 1e-3 开始，使用学习率调度器
3. **早停**: 监控验证集损失，避免过拟合
4. **检查点**: 定期保存模型检查点

### 推理部署

1. **模型优化**: 使用 TorchScript 或 ONNX 优化推理速度
2. **批处理**: 尽可能使用批量推理提高效率
3. **缓存**: 对重复查询结果进行缓存
4. **监控**: 监控 API 响应时间和错误率

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

## 📄 许可证

MIT License

## 📧 联系

如有问题，请提交 Issue 或联系开发团队。

---

**AstroAI-Core** - 让 AI 探索宇宙 🌌
