# AstroAI-Core

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Status: Development](https://img.shields.io/badge/status-development-orange.svg)]()
[![GitHub Stars](https://img.shields.io/github/stars/AstroAI-Core/AstroAI-Core.svg)](https://github.com/AstroAI-Core/AstroAI-Core/stargazers)
[![Issues](https://img.shields.io/github/issues/AstroAI-Core/AstroAI-Core.svg)](https://github.com/AstroAI-Core/AstroAI-Core/issues)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

<div align="center">

**🌌 AI 驱动的天文数据分析平台 | AI-Powered Astronomy Data Analysis Platform**

结合深度学习与天文数据，帮助爱好者和研究人员自动发现系外行星、分类恒星、识别异常天体

[🚀 快速开始](#-快速开始) · [📚 文档](#-文档) · [✨ 功能特性](#-功能特性) · [🤝 贡献指南](#-贡献指南) · [💬 社区](#-社区)

![AstroAI Demo](./docs/assets/demo.png)
*图：AstroAI-Core 系外行星探测演示界面*

</div>

---

## 🌟 项目简介

AstroAI-Core 是一个开源的天文数据分析平台，利用先进的深度学习技术处理 TESS/Kepler 等望远镜的海量观测数据，让每个人都能轻松探索宇宙奥秘。

### 核心价值

| 痛点 | AstroAI-Core 解决方案 |
|------|----------------------|
| 🔭 天文数据处理复杂 | 一键式自动化分析流程 |
| 📊 机器学习门槛高 | 预训练模型 + 友好 API |
| 🌌 数据源分散 | 统一集成 NASA/ESA 等权威数据源 |

---

## ✨ 功能特性

### 核心能力

| 功能 | 描述 | 状态 |
|------|------|------|
| 🔭 **系外行星探测** | 自动从 TESS/Kepler 光变曲线中检测凌日信号 | 🚧 开发中 |
| ⭐ **恒星分类** | AI 驱动的恒星光谱分类 (OBAFGKM) | 📋 规划中 |
| 🌌 **异常识别** | 发现稀有和不寻常的天体 | 📋 规划中 |
| 📊 **光谱分析** | 自动化光谱分析和红移测量 | 📋 规划中 |
| 🎨 **交互可视化** | 3D 星图和图表展示 | 📋 规划中 |
| 🔌 **RESTful API** | 所有功能的编程访问接口 | 📋 规划中 |

---

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git

### 5 分钟快速体验

```bash
# 1. 克隆项目
git clone https://github.com/AstroAI-Core/AstroAI-Core.git
cd AstroAI-Core

# 2. 设置后端
cd api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. 设置前端
cd ../frontend
npm install

# 4. 启动开发环境
cd ..
docker-compose up -d
```

### 生产部署

```bash
# Docker Compose 部署
docker-compose -f docker-compose.prod.yml up -d

# Kubernetes 部署
kubectl apply -f deployments/k8s/
```

访问地址：
- 🌐 前端：http://localhost:3000
- 📡 API：http://localhost:8000
- 📖 文档：http://localhost:8000/docs

---

## 📖 使用示例

### Python SDK

```python
from astroai import AstroAIClient

# 初始化客户端
client = AstroAIClient(api_key="your_api_key")

# 分析光变曲线
result = client.analyze_lightcurve(
    data=[...],  # 你的流量测量数据
    cadence=1800  # 秒
)
print(f"系外行星概率：{result.planet_probability:.2%}")
print(f"估计周期：{result.period:.2f} 天")

# 分类恒星图像
result = client.classify_image("star_photo.png")
print(f"光谱类型：{result.spectral_type}")
print(f"光度等级：{result.luminosity_class}")
```

### REST API

```bash
# 分析光变曲线
curl -X POST http://localhost:8000/api/v1/analyze/lightcurve \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"data": [...], "cadence": 1800}'

# 获取天体信息
curl http://localhost:8000/api/v1/objects/TOI-700 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                      客户端层                                │
│         Web 应用 │ 移动应用 │ CLI │ API 客户端               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    API 网关                                  │
│              认证 │ 限流 │ 路由                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   微服务层                                   │
│    数据服务 │ 模型服务 │ 用户服务 │ 任务服务                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     数据层                                   │
│        PostgreSQL │ Redis │ MinIO/S3 │ DuckDB               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  外部数据源                                   │
│         NASA API │ ESA API │ SDSS │ 其他档案库              │
└─────────────────────────────────────────────────────────────┘
```

### 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **前端** | React 18 + TypeScript + Three.js | 3D 可视化界面 |
| **后端** | Python 3.11 + FastAPI | 高性能异步 API |
| **AI 框架** | PyTorch 2.0 + HuggingFace | 深度学习模型 |
| **数据库** | PostgreSQL 15 + Redis 7 | 关系型 + 缓存 |
| **存储** | MinIO / AWS S3 | 对象存储 |
| **部署** | Docker + Kubernetes | 容器化编排 |
| **监控** | Prometheus + Grafana | 可观测性 |

---

## 📚 文档

| 文档 | 说明 | 链接 |
|------|------|------|
| 📘 安装指南 | 详细安装步骤 | [查看](docs/installation.md) |
| 📗 快速入门 | 5 分钟上手教程 | [查看](docs/quickstart.md) |
| 📙 API 参考 | 完整 API 文档 | [查看](docs/api.md) |
| 📕 示例代码 | 实用示例集合 | [查看](examples/) |
| 📒 贡献指南 | 如何贡献代码 | [查看](CONTRIBUTING.md) |

---

## 🗺️ 路线图

<div align="center">

| 时间 | 里程碑 | 状态 |
|------|--------|------|
| 2026 Q2 | MVP 版本：核心 ML 模型 + 基础 API | ✅ 进行中 |
| 2026 Q3 | 功能完整：图像分类 + 异常检测 | 📋 规划中 |
| 2026 Q4 | 生产就绪：性能优化 + 安全加固 | 📋 规划中 |
| 2027 Q1 | 公开发布：Beta 测试 + 社区建设 | 📋 规划中 |

</div>

详细路线图请查看 [ROADMAP.md](docs/ROADMAP.md)

---

## 🤝 贡献指南

我们欢迎各种形式的贡献！

### 如何贡献

1. 🍴 **Fork 仓库** - 创建你自己的 fork
2. 🌿 **创建分支** - `git checkout -b feature/amazing-feature`
3. 💻 **开发** - 编写代码和测试
4. ✅ **测试** - 确保所有测试通过
5. 📤 **提交 PR** - 描述你的改动

### 开发环境设置

```bash
# Fork & Clone
git clone https://github.com/YOUR_USERNAME/AstroAI-Core.git
cd AstroAI-Core

# 安装依赖
cd api && pip install -r requirements.txt
cd ../frontend && npm install

# 运行测试
pytest tests/ -v
npm run test
```

### 代码规范

- **Python:** 遵循 PEP 8 + Black 格式化
- **TypeScript:** 遵循 ESLint + Prettier
- **提交信息:** 遵循 Conventional Commits 规范

详见 [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 🧪 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定模块测试
pytest tests/test_lightcurve.py -v
pytest tests/test_classification.py -v

# 带覆盖率报告
pytest --cov=astroai --cov-report=html
```

---

## 📊 项目统计

[![Star History](https://api.star-history.com/svg?repos=AstroAI-Core/AstroAI-Core&type=Date)](https://star-history.com/#AstroAI-Core/AstroAI-Core&Date)

| 指标 | 数据 |
|------|------|
| ⭐ Stars | 0 |
| 🍴 Forks | 0 |
| 🐛 Issues | 0 |
| 📦 Downloads | 0 |

---

## 💬 社区

### 联系方式

| 平台 | 链接 |
|------|------|
| 🌐 官网 | https://astroai-core.com (即将上线) |
| 📧 邮箱 | contact@astroai-core.dev |
| 💬 Discord | [加入社区](https://discord.gg/astroai) |
| 🐦 Twitter | [@AstroAI_Core](https://twitter.com/AstroAI_Core) |
| 📱 微信 | AstroAI 实验室 |
| 📺 B 站 | @AstroAI-Core |

### 加入讨论

- 💬 **Discord 服务器**: [点击加入](https://discord.gg/astroai)
- 📱 **微信群**: 添加小助手微信 `astroai_helper` 邀请入群
- 🐦 **Twitter**: [@AstroAI_Core](https://twitter.com/AstroAI_Core)
- 📺 **B 站**: [@AstroAI-Core](https://space.bilibili.com/astroai)

---

## 💰 赞助商

AstroAI-Core 是开源项目，感谢以下赞助商的支持：

<div align="center">

| 赞助商等级 | 赞助商 | 链接 |
|-----------|--------|------|
| 🏆 **金牌赞助商** | [虚位以待] | [成为赞助商](mailto:sponsor@astroai-core.com) |
| 🥈 **银牌赞助商** | [虚位以待] | [成为赞助商](mailto:sponsor@astroai-core.com) |
| 🥉 **铜牌赞助商** | [虚位以待] | [成为赞助商](mailto:sponsor@astroai-core.com) |

</div>

### 赞助方式

我们接受以下形式的赞助：

- 💰 **资金赞助** - 支持项目持续开发
- 🖥️ **云服务资源** - 服务器、存储、CDN
- 🎯 **推广支持** - 社交媒体分享、技术文章
- 👨‍💻 **人才赞助** - 开发者贡献时间

[👉 立即赞助](https://github.com/sponsors/AstroAI-Core) | [📧 联系合作](mailto:sponsor@astroai-core.com)

---

## 🙏 致谢

感谢以下优秀的开源项目：

- [NASA Exoplanet Archive](https://exoplanetarchive.ipac.caltech.edu/) - 开放数据访问
- [ESA Gaia](https://www.cosmos.esa.int/web/gaia) - 恒星目录
- [TESS](https://tess.mit.edu/) - 凌日系外行星勘测卫星
- [PyTorch](https://pytorch.org/) - 深度学习框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代 Python Web 框架

---

## 📄 许可证

本项目采用 **MIT 许可证** - 详见 [LICENSE](LICENSE) 文件

---

## 👥 团队

- **创始人**: 志哥
- **核心团队**: AstroAI 开发团队
- **贡献者**: [查看贡献者列表](https://github.com/AstroAI-Core/AstroAI-Core/graphs/contributors)

---

<div align="center">

### ⭐ 喜欢这个项目吗？

如果这个项目对你有帮助，请给我们一个 **Star** 支持！你的支持是我们持续开发的动力！

[![Star](https://img.shields.io/github/stars/AstroAI-Core/AstroAI-Core?style=social)](https://github.com/AstroAI-Core/AstroAI-Core)

---

**Made with ❤️ by the AstroAI Team**

🌟 *用 AI 探索宇宙* 🌟

[⬆ 返回顶部](#astroai-core)

</div>

---

## 🔍 SEO 关键词

AstroAI-Core, 天文数据分析，系外行星探测，AI 天文，机器学习天文，深度学习太空，open source, AI, machine learning, deep learning, astronomy, exoplanet
