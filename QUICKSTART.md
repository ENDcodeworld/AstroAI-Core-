# AstroAI-Core 快速开始指南

## 🎯 Phase 1 完成内容

✅ **图像分类模型架构**
- `ml/models/star_classifier.py` - ResNet/ViT 双架构支持
- 支持 3 大类（恒星/星系/星云）+ 10 细分类
- 置信度评分系统

✅ **数据加载器**
- `ml/data_loader.py` - Hubble 数据集支持
- 数据增强（旋转、翻转、缩放）
- 自动训练/验证/测试集划分

✅ **训练管道**
- `ml/train_classifier.py` - 完整训练流程
- 混合精度训练、早停、学习率调度
- 训练日志和可视化

✅ **推理 API**
- `ml/inference.py` - 高效推理引擎
- 单张/批量/base64 推理
- 结果导出（JSON/CSV）

✅ **REST API**
- `api/app/api/v1/classify.py` - FastAPI 端点
- 图像上传、批量分类接口
- 健康检查和类别查询

✅ **测试和文档**
- `tests/test_classifier.py` - 完整测试套件
- `ml/README.md` - 详细使用文档

## 🚀 快速使用

### 1. 安装依赖

```bash
cd /home/admin/.openclaw/workspace/projects/AstroAI-Core
pip install -r requirements.txt
```

### 2. 准备数据

```bash
# 将 Hubble 图像按类别放入 data 目录
mkdir -p data/{star,galaxy,nebula}
# 复制图像到对应目录...
```

### 3. 训练模型

```bash
cd ml
python train_classifier.py
```

或使用 Python API:

```python
from ml.train_classifier import TrainingConfig, Trainer
from ml.data_loader import create_data_loaders

config = TrainingConfig(
    data_dir='./data',
    epochs=50,
    batch_size=32
)

trainer = Trainer(config)
train_loader, val_loader, _ = create_data_loaders('./data')
trainer.train(train_loader, val_loader)
```

### 4. 推理使用

```python
from ml.inference import InferenceEngine

# 加载训练好的模型
engine = InferenceEngine('./ml/checkpoints/best_model.pth')

# 分类图像
result = engine.predict('my_galaxy_image.jpg')
print(f"类别：{result['best_main_category']}")
print(f"置信度：{result['overall_confidence']:.2%}")
```

### 5. 启动 API 服务

```bash
cd /home/admin/.openclaw/workspace/projects/AstroAI-Core
uvicorn api.app.main:app --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/docs 查看 API 文档

### 6. 运行测试

```bash
cd tests
python test_classifier.py
```

## 📊 预期性能

使用 Hubble 数据集训练后，预期达到:

| 指标 | 目标值 |
|------|--------|
| 主类别准确率 | >90% |
| 细分类准确率 | >80% |
| 推理速度 (单张) | <100ms |
| 推理速度 (批量) | <50ms/张 |

## 📁 关键文件

```
AstroAI-Core/
├── ml/
│   ├── models/star_classifier.py    # ⭐ 核心模型
│   ├── data_loader.py               # 📊 数据加载
│   ├── train_classifier.py          # 🎯 训练管道
│   ├── inference.py                 # 🔮 推理引擎
│   └── README.md                    # 📖 详细文档
├── api/app/api/v1/classify.py       # 🌐 REST API
├── tests/test_classifier.py         # 🧪 测试套件
└── requirements.txt                 # 📦 依赖
```

## 🎓 下一步

Phase 2 规划:
- [ ] 集成 Hubble API 自动获取数据
- [ ] 实现主动学习流程
- [ ] 添加模型解释性 (Grad-CAM)
- [ ] 部署到生产环境

## 💡 使用技巧

1. **数据质量优先**: 确保训练图像清晰、标签准确
2. **数据增强**: 使用 `DataAugmenter` 扩充小数据集
3. **迁移学习**: 始终使用预训练权重加速收敛
4. **监控训练**: 查看 `logs/training_curves.png` 了解训练状态
5. **批量推理**: 处理多张图像时使用 `predict_batch` 提高效率

## 🆘 常见问题

**Q: CUDA out of memory?**
A: 减小 `batch_size` 或使用 `mixed_precision=True`

**Q: 准确率低？**
A: 检查数据质量，增加训练轮数，调整学习率

**Q: 推理速度慢？**
A: 使用批量推理，考虑模型量化或 ONNX 优化

---

**AstroAI-Core Phase 1** - 图像分类功能已完成！🎉
