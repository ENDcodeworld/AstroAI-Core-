<div align="center">

# 🔭 AstroAI-Core

**AI-Powered Astronomy & Astrophysics Toolkit**

[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

天文 AI 工具包，用机器学习探索星空

</div>

## 🎯 研究方向

| 方向 | 描述 | 状态 |
|:-----|:-----|:-----:|
| 🔍 天体识别 | AI 自动识别天体类型 | ✅ |
| 📊 光谱分析 | 恒星光谱自动分类 | ✅ |
| 🪐 行星搜索 | 系外行星信号检测 | ✅ |
| 🌟 变星检测 | 光变曲线分析 | ✅ |
| 🗺️ 星图生成 | 天文数据可视化 | ✅ |

## 🚀 核心功能

### 1. 🔭 系外行星检测
使用 BLS (Box Least Squares) 算法检测行星凌日信号

```python
from src.exoplanet_detector import TransitDetector, StellarParameters

# 检测凌日信号
detector = TransitDetector()
result = detector.box_least_squares(time, flux)

print(f"检测周期: {result['period_days']:.3f} 天")
print(f"凌日深度: {result['depth_ppm']:.0f} ppm")
print(f"信噪比: {result['snr']:.1f}")

# 计算行星参数
params = StellarParameters()
radius = params.calculate_planet_radius(result['depth_ppm']/1e6, stellar_radius=1.0)
a = params.calculate_semi_major_axis(result['period_days'])
temp = params.estimate_equilibrium_temperature(5778, 1.0, a)
```

### 2. ⭐ 恒星光谱分类
基于哈佛分类系统自动识别恒星光谱型

```python
from src.spectral_classifier import SpectralClassifier

classifier = SpectralClassifier()

# 使用颜色指数分类
result = classifier.classify_by_color_indices(u_mag, g_mag, r_mag, i_mag)
print(f"光谱型: {result['spectral_type']}")
print(f"估计温度: {result['estimated_temperature']} K")

# 使用光谱数据详细分类
result = classifier.classify_by_spectrum(wavelength, flux)
print(f"完整光谱型: {result['full_type']}")
print(f"置信度: {result['confidence']*100:.1f}%")
```

### 3. 📊 天文数据可视化

```python
from src.astro_visualization import LightCurvePlotter, SpectrumPlotter

# 光变曲线
lc_plotter = LightCurvePlotter()
lc_plotter.plot_lightcurve(time, flux, period=5.0, phase_fold=True)
lc_plotter.plot_folded_transits(time, flux, period, t0, duration)

# 光谱
spec_plotter = SpectrumPlotter()
spec_plotter.plot_spectrum(wavelength, flux, spectral_lines={'Hα': 6563})
```

### 4. 🤖 天体图像分类 (ML模块)

```python
from ml.inference import InferenceEngine

engine = InferenceEngine(model_path='./ml/checkpoints/best_model.pth')
result = engine.predict('galaxy_image.jpg')

print(f"类别: {result['best_main_category']}")
print(f"置信度: {result['overall_confidence']:.2%}")
```

## 📁 项目结构

```
AstroAI-Core/
├── src/
│   ├── exoplanet_detector.py      # 系外行星检测
│   ├── spectral_classifier.py     # 光谱分类
│   ├── astro_visualization.py     # 数据可视化
│   └── ...
├── ml/                             # 机器学习模块
│   ├── data_loader.py
│   ├── train_classifier.py
│   ├── inference.py
│   └── models/
├── api/                            # FastAPI后端
│   └── app/
├── frontend/                       # 前端界面
├── tests/                          # 测试
└── docs/                           # 文档
```

## 🧪 快速测试

```bash
# 测试系外行星检测
python src/exoplanet_detector.py

# 测试光谱分类
python src/spectral_classifier.py

# 测试可视化
python src/astro_visualization.py

# 测试ML分类器
python ml/inference.py
```

## 📚 参考资源

- [Astropy](https://www.astropy.org/) - Python 天文学核心库
- [SIMBAD](https://simbad.u-strasbg.fr/) - 天文数据库
- [NASA Exoplanet Archive](https://exoplanetarchive.ipac.caltech.edu/)
- [TESS](https://tess.mit.edu/) - 凌日系外行星巡天卫星

## 📜 License

[MIT](LICENSE)

---

**Made with ❤️ by AI 前沿社**
