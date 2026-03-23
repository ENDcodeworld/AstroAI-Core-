# 🔭 AstroAI-Core

**AI-Powered Astronomy & Astrophysics Toolkit**

[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-red?style=flat-square&logo=pytorch)](https://pytorch.org)

天文 AI 工具包，用机器学习探索星空

</div>

---

## 📋 目录

- [功能特性](#功能特性)
- [快速开始](#快速开始)
- [核心模块](#核心模块)
- [API文档](#api文档)
- [使用教程](#使用教程)
- [项目结构](#项目结构)
- [模型训练](#模型训练)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

---

## ✨ 功能特性

### 🔭 系外行星检测
- **BLS算法**：Box Least Squares周期性信号检测
- **凌日拟合**：梯形模型拟合凌日参数
- **假阳性筛选**：自动识别食双星等干扰信号

### ⭐ 恒星光谱分析
- **光谱分类**：基于哈佛分类系统的自动分类
- **颜色指数**：使用测光数据进行快速分类
- **物理参数**：估算温度、质量、半径、光度

### 🤖 AI天体识别
- **深度学习**：ResNet50 + Vision Transformer架构
- **多标签分类**：恒星、星系、星云自动识别
- **细分类**：星系形态、星云类型细分

### 📊 数据可视化
- **光变曲线**：支持相位折叠和凌日展示
- **光谱绘图**：特征谱线标注
- **星图绘制**：赤经赤纬投影、星座连线

---

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/ENDcodeworld/AstroAI-Core-.git
cd AstroAI-Core-

# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装基础依赖
pip install -r requirements.txt

# 安装机器学习依赖（可选）
pip install torch torchvision
```

### 快速测试

```bash
# 测试系外行星检测
python src/exoplanet_detector.py

# 测试光谱分类
python src/spectral_classifier.py

# 测试可视化
python src/astro_visualization.py
```

---

## 📦 核心模块

### 1. 系外行星检测

检测恒星亮度周期性下降，发现系外行星候选体：

```python
from src.exoplanet_detector import TransitDetector, StellarParameters, PlanetValidator
import numpy as np

# 创建检测器
detector = TransitDetector()

# 准备数据（时间：天，流量：归一化）
time = np.linspace(0, 90, 9000)  # 90天观测
flux = np.ones_like(time)

# 添加模拟凌日信号
period = 10.5  # 轨道周期
depth = 0.001  # 凌日深度 0.1%
for t0 in np.arange(5, 90, period):
    mask = np.abs(time - t0) < 0.15
    flux[mask] *= (1 - depth)

# 添加噪声
flux += np.random.normal(0, 0.0005, len(flux))

# 运行BLS检测
result = detector.box_least_squares(time, flux)

print("=" * 50)
print("📋 检测结果")
print("=" * 50)
print(f"检测周期: {result['period_days']:.3f} 天")
print(f"凌日深度: {result['depth_ppm']:.0f} ppm")
print(f"持续时间: {result['duration_hours']:.2f} 小时")
print(f"信噪比: {result['snr']:.1f}")
print(f"行星候选体: {'✅ 是' if result['is_planet_candidate'] else '❌ 否'}")

# 计算行星参数
params = StellarParameters()
planet_radius = params.calculate_planet_radius(
    result['depth_ppm']/1e6, 
    stellar_radius=1.0  # 太阳半径
)
semi_major_axis = params.calculate_semi_major_axis(
    result['period_days'],
    stellar_mass=1.0  # 太阳质量
)
equilibrium_temp = params.estimate_equilibrium_temperature(
    stellar_temp=5778,  # K
    stellar_radius=1.0,
    semi_major_axis=semi_major_axis
)

print(f"\n🌍 行星参数")
print(f"估算半径: {planet_radius:.2f} 地球半径")
print(f"轨道半长轴: {semi_major_axis:.3f} AU")
print(f"平衡温度: {equilibrium_temp:.0f} K")

# 验证结果
validator = PlanetValidator()
passed, checks = validator.validate(result)
print(f"\n✅ 验证结果: {'通过' if passed else '未通过'}")
for check in checks:
    print(f"  {check}")
```

### 2. 恒星光谱分类

基于光谱数据自动分类恒星：

```python
from src.spectral_classifier import SpectralClassifier, generate_mock_spectrum

classifier = SpectralClassifier()

# 方法1: 使用颜色指数快速分类
# u, g, r, i 是不同波段的星等
result = classifier.classify_by_color_indices(
    u_mag=15.0,
    g_mag=13.5,
    r_mag=12.8,
    i_mag=12.3
)

print(f"光谱型: {result['spectral_type']}")
print(f"估计温度: {result['estimated_temperature']:,} K")
print(f"颜色指数 u-g: {result['color_indices']['u-g']:.2f}")

# 方法2: 使用光谱数据详细分类
wavelength, flux = generate_mock_spectrum('G', sub_type=2)

result = classifier.classify_by_spectrum(wavelength, flux)

print(f"\n详细分类结果:")
print(f"完整光谱型: {result['full_type']}")
print(f"置信度: {result['confidence']*100:.1f}%")
print(f"有效温度: {result['physical_parameters']['effective_temperature_k']:,} K")
print(f"质量: {result['physical_parameters']['mass_solar']} M☉")
print(f"半径: {result['physical_parameters']['radius_solar']} R☉")
print(f"光度: {result['physical_parameters']['luminosity_solar']} L☉")
```

### 3. 天文数据可视化

```python
from src.astro_visualization import (
    LightCurvePlotter, 
    SpectrumPlotter, 
    SkyMapPlotter,
    HRDiagramPlotter
)
import numpy as np

# ========== 光变曲线 ==========
lc_plotter = LightCurvePlotter()

# 生成示例数据
time = np.linspace(0, 30, 3000)
flux = np.ones_like(time)

# 添加周期性凌日
period = 5.0
for t0 in np.arange(2.5, 30, period):
    mask = np.abs(time - t0) < 0.1
    flux[mask] *= 0.99

flux += np.random.normal(0, 0.001, len(flux))

# 绘制原始光变曲线
lc_plotter.plot_lightcurve(
    time, flux,
    title="Exoplanet Transit Light Curve",
    save_path="lightcurve.png"
)

# 绘制相位折叠曲线
lc_plotter.plot_folded_transits(
    time, flux,
    period=5.0, t0=2.5, duration=3.0,
    save_path="folded_transit.png"
)

# ========== 光谱绘图 ==========
spec_plotter = SpectrumPlotter()

wavelength = np.linspace(4000, 7000, 3000)
flux_spec = np.ones_like(wavelength)

# 添加Balmer线
for line in [4102, 4340, 4861, 6563]:
    mask = np.abs(wavelength - line) < 20
    flux_spec[mask] *= (1 - 0.1 * np.exp(-((wavelength[mask]-line)/5)**2))

spectral_lines = {
    'Hδ': 4102, 'Hγ': 4340,
    'Hβ': 4861, 'Hα': 6563
}

spec_plotter.plot_spectrum(
    wavelength, flux_spec,
    spectral_lines=spectral_lines,
    title="Stellar Spectrum",
    save_path="spectrum.png"
)

# ========== 赫罗图 ==========
hr_plotter = HRDiagramPlotter()

# 模拟恒星数据
color_index = np.random.normal(0.6, 0.4, 1000)
abs_mag = np.random.normal(5, 3, 1000)
spectral_types = np.random.choice(['O', 'B', 'A', 'F', 'G', 'K', 'M'], 1000)

hr_plotter.plot_hr_diagram(
    color_index, abs_mag, spectral_types,
    title="Hertzsprung-Russell Diagram",
    save_path="hr_diagram.png"
)
```

### 4. ML天体分类

```python
from ml.inference import InferenceEngine

# 加载预训练模型
engine = InferenceEngine(model_path='./ml/checkpoints/best_model.pth')

# 单张图像分类
result = engine.predict('galaxy_image.jpg')

print(f"最佳类别: {result['best_main_category']}")
print(f"细分类别: {result['best_sub_category']}")
print(f"置信度: {result['overall_confidence']:.2%}")

# 显示所有预测
for pred in result['main_predictions']:
    print(f"  {pred['category']}: {pred['probability']:.2%}")

# 批量预测
images = ['star1.jpg', 'galaxy1.jpg', 'nebula1.jpg']
results = engine.predict_batch(images)

# 导出结果
engine.export_results(results, 'predictions.json', format='json')
```

---

## 📚 API文档

### 系外行星检测

#### `TransitDetector`

| 方法 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `box_least_squares` | time, flux, flux_err | Dict | BLS算法检测 |
| `fit_transit_model` | time, flux, period, t0 | Dict | 拟合凌日模型 |

#### `StellarParameters`

| 方法 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `calculate_planet_radius` | depth, stellar_radius | float | 计算行星半径 |
| `calculate_semi_major_axis` | period, stellar_mass | float | 计算半长轴 |
| `estimate_equilibrium_temperature` | T_star, R_star, a | float | 估算平衡温度 |

### 光谱分类

#### `SpectralClassifier`

| 方法 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `classify_by_color_indices` | u,g,r,i magnitudes | Dict | 颜色指数分类 |
| `classify_by_spectrum` | wavelength, flux | Dict | 光谱数据分类 |

---

## 🎯 使用教程

### 教程1：发现系外行星

```python
"""
完整教程：从TESS光变曲线中发现系外行星
"""
import numpy as np
from src.exoplanet_detector import TransitDetector

# 1. 加载TESS数据（示例）
# 实际使用：from lightkurve import search_lightcurve
time = np.linspace(0, 27, 10000)  # TESS一个sector约27天
flux = np.ones_like(time)

# 2. 添加模拟行星信号
planet_period = 3.5  # 天
planet_depth = 0.002  # 0.2%

for t0 in np.arange(1, 27, planet_period):
    mask = np.abs(time - t0) < 0.12
    flux[mask] *= (1 - planet_depth)

# 3. 添加恒星噪声
flux += np.random.normal(0, 0.0003, len(flux))

# 4. 运行检测
detector = TransitDetector()
result = detector.box_least_squares(time, flux)

# 5. 验证
if result['is_planet_candidate']:
    print(f"🎉 发现行星候选体!")
    print(f"   周期: {result['period_days']:.3f} 天")
    print(f"   半径: {np.sqrt(result['depth_ppm']/1e6)*109:.1f} 地球半径")
```

### 教程2：恒星光谱分析

```python
"""
光谱分类教程
"""
from src.spectral_classifier import SpectralClassifier

classifier = SpectralClassifier()

# 测试不同光谱型的恒星
test_stars = [
    ('天狼星', 11.0, 10.0, 9.5, 9.2),      # A型
    ('太阳', 15.0, 13.5, 12.8, 12.3),       # G型
    ('心宿二', 18.0, 15.0, 12.5, 11.0),     # M型
]

for name, u, g, r, i in test_stars:
    result = classifier.classify_by_color_indices(u, g, r, i)
    temp_range = result['temperature_range']
    
    print(f"{name}: {result['spectral_type']}型")
    print(f"   温度: {temp_range[0]:,} - {temp_range[1]:,} K")
```

---

## 🏗️ 项目结构

```
AstroAI-Core-
├── src/                          # 核心源码
│   ├── exoplanet_detector.py     # 系外行星检测
│   ├── spectral_classifier.py    # 光谱分类
│   └── astro_visualization.py    # 数据可视化
├── ml/                           # 机器学习模块
│   ├── data_loader.py            # 数据加载
│   ├── train_classifier.py       # 训练脚本
│   ├── inference.py              # 推理引擎
│   └── models/                   # 模型定义
│       └── star_classifier.py
├── api/                          # FastAPI后端
│   └── app/
├── frontend/                     # 前端界面
├── tests/                        # 测试
├── data/                         # 数据集
└── docs/                         # 文档
```

---

## 🧠 模型训练

### 训练天体分类器

```bash
# 准备数据
# 将图像按类别放入 data/ 目录
# data/star/, data/galaxy/, data/nebula/

# 训练模型
cd ml
python train_classifier.py \
    --data_dir ../data/celestial \
    --epochs 50 \
    --batch_size 32 \
    --model_type resnet

# 模型将保存到 ml/checkpoints/best_model.pth
```

### 训练配置

```python
from ml.train_classifier import TrainingConfig

config = TrainingConfig(
    model_type='resnet',        # 或 'vit'
    epochs=100,
    batch_size=64,
    learning_rate=1e-3,
    pretrained=True,            # 使用ImageNet预训练
    mixed_precision=True,       # 混合精度训练
    early_stopping=True,
    patience=10
)
```

---

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 代码规范

- 遵循 PEP 8 风格指南
- 添加文档字符串
- 编写单元测试

---

## 📖 参考资料

- [TESS任务](https://tess.mit.edu/) - 凌日系外行星巡天
- [Kepler任务](https://www.nasa.gov/mission_pages/kepler/main/index.html)
- [NASA Exoplanet Archive](https://exoplanetarchive.ipac.caltech.edu/)
- [SIMBAD天文数据库](http://simbad.u-strasbg.fr/simbad/)
- [Astropy](https://www.astropy.org/) - Python天文库

---

## 📜 许可证

[MIT](LICENSE)

---

<div align="center">

**Made with ❤️ by AI 前沿社**

⭐ Star 支持我们！

</div>
