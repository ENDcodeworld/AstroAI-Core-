# AstroAI-Core Demo on HuggingFace Spaces

## 部署步骤

### 方法 1: 通过 HuggingFace 网页上传

1. 访问 https://huggingface.co/spaces
2. 点击 "Create new Space"
3. 填写信息：
   - Space name: `AstroAI-Core-Demo`
   - License: MIT
   - SDK: Gradio
   - Visibility: Public
4. 创建后，上传以下文件：
   - `gradio_app.py` (重命名为 `app.py`)
   - `requirements.txt`

### 方法 2: 通过 Git 推送

```bash
# 克隆你的 Space
git clone https://huggingface.co/spaces/ENDcodeworld/AstroAI-Core-Demo
cd AstroAI-Core-Demo

# 复制 Demo 文件
cp /home/admin/.openclaw/workspace/projects/AstroAI-Core/demo/gradio_app.py app.py
cp /home/admin/.openclaw/workspace/projects/AstroAI-Core/demo/requirements.txt .

# 提交并推送
git add .
git commit -m "Initial commit: AstroAI-Core transit detection demo"
git push
```

### 方法 3: 使用 HuggingFace Hub CLI

```bash
# 安装 huggingface_hub
pip install huggingface_hub

# 登录
huggingface-cli login

# 上传文件
huggingface-cli upload ENDcodeworld/AstroAI-Core-Demo \
  /home/admin/.openclaw/workspace/projects/AstroAI-Core/demo/gradio_app.py \
  app.py

huggingface-cli upload ENDcodeworld/AstroAI-Core-Demo \
  /home/admin/.openclaw/workspace/projects/AstroAI-Core/demo/requirements.txt \
  requirements.txt
```

## Space 配置

创建 `README.md` for the Space:

```markdown
---
title: AstroAI-Core Demo
emoji: 🌌
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.0.0
app_file: app.py
pinned: false
license: mit
---

# 🌌 AstroAI-Core 系外行星探测 Demo

体验 AI 驱动的天文数据分析！

## 功能

- 模拟系外行星凌日光变曲线
- 自动检测凌日信号
- 交互式参数调整
- 实时可视化

## 关于项目

AstroAI-Core 是一个开源的天文数据分析平台。

🔗 GitHub: https://github.com/ENDcodeworld/AstroAI-Core

## 使用

1. 调整噪声水平、行星大小和数据点数量
2. 点击"分析光变曲线"
3. 查看检测结果
```

## 验证部署

部署完成后，访问：
https://huggingface.co/spaces/ENDcodeworld/AstroAI-Core-Demo

## 更新 README

在 AstroAI-Core 主项目的 README.md 中添加：

```markdown
## 🎮 在线 Demo

试试我们的交互式 Demo：[AstroAI-Core on HuggingFace Spaces](https://huggingface.co/spaces/ENDcodeworld/AstroAI-Core-Demo)
```
