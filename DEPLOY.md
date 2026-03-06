# 🚀 AstroAI-Core 外部部署指南

**目标**：让天文学项目可以通过公网访问

---

## 📋 部署架构

```
┌─────────────┐         ┌─────────────┐
│   Vercel    │         │   Railway   │
│   (前端)    │ ──────→ │  (后端+DB)  │
│  免费托管   │  API    │  $5/月      │
└─────────────┘         └─────────────┘
      ↓                       ↓
  astroai.vercel.app    api.railway.app
```

---

## 第 1 步：部署后端到 Railway

### 1.1 创建 Railway 账号
1. 访问：https://railway.app/
2. 点击 "Start a New Project"
3. 用 GitHub 登录

### 1.2 创建新项目
1. 点击 "New Project"
2. 选择 "Deploy from GitHub repo"
3. 选择 `AstroAI-Core` 仓库

### 1.3 配置后端服务
1. 在 Railway 面板，点击 "New" → "Empty Service"
2. 设置 Build Command：
   ```bash
   pip install -r api/requirements.txt
   ```
3. 设置 Start Command：
   ```bash
   uvicorn api.app.main:app --host 0.0.0.0 --port $PORT
   ```

### 1.4 添加环境变量
在 Railway 面板添加以下变量：
```
NASA_API_KEY=RKKPoomDvkCh0COjlDbWZ1deUAwuA68wzvYFhvoo
DATABASE_URL=postgresql://postgres:password@postgres.railway.internal:5432/railway
REDIS_URL=redis://redis.railway.internal:6379
```

### 1.5 添加 PostgreSQL 数据库
1. 点击 "New" → "Database" → "PostgreSQL"
2. Railway 会自动创建数据库
3. 复制 DATABASE_URL 到环境变量

### 1.6 部署完成
- Railway 会自动构建和部署
- 获得公网 URL：`https://your-app.railway.app`
- 测试 API：`https://your-app.railway.app/api/v1/exoplanets`

**预计时间**：15-20 分钟
**费用**：$5/月（含数据库）

---

## 第 2 步：部署前端到 Vercel

### 2.1 创建 Vercel 账号
1. 访问：https://vercel.com/
2. 点击 "Sign Up"
3. 用 GitHub 登录

### 2.2 导入项目
1. 点击 "Add New Project"
2. 选择 "Import Git Repository"
3. 选择 `AstroAI-Core/frontend` 目录

### 2.3 配置构建设置
- **Framework Preset**：Vite
- **Build Command**：`npm run build`
- **Output Directory**：`dist`

### 2.4 添加环境变量
在 Vercel 面板添加：
```
VITE_API_URL=https://your-railway-app.railway.app/api/v1
```

### 2.5 部署
1. 点击 "Deploy"
2. Vercel 会自动构建和部署
3. 获得公网 URL：`https://astroai.vercel.app`

**预计时间**：10-15 分钟
**费用**：免费

---

## 第 3 步：测试和验证

### 3.1 访问前端
```
https://astroai.vercel.app
```

### 3.2 测试 API
```
https://your-railway-app.railway.app/api/v1/exoplanets
```

### 3.3 测试图像分类
```
https://your-railway-app.railway.app/api/v1/classify
```

---

## 📊 费用总结

| 服务 | 费用 | 说明 |
|------|------|------|
| Vercel | 免费 | 前端静态托管 |
| Railway | $5/月 | 后端 + PostgreSQL |
| **总计** | **$5/月** | 约¥36/月 |

---

## 🔧 备选方案

### 方案 B：Render（类似 Railway）
- 网址：https://render.com/
- 价格：$7/月
- 优点：免费 PostgreSQL

### 方案 C：阿里云轻量服务器
- 价格：¥60-100/月
- 优点：国内访问快，备案后可用
- 缺点：需要手动配置环境

### 方案 D：腾讯云云开发
- 价格：¥19/月起
- 优点：一键部署，国内访问快
- 网址：https://cloud.tencent.com/product/tcb

---

## 📞 需要帮助？

遇到问题可以：
1. 查看 Railway 日志：https://railway.app/dashboard
2. 查看 Vercel 日志：https://vercel.com/dashboard
3. 检查 API 文档：https://your-railway-app.railway.app/docs

---

*最后更新：2026-03-06*
