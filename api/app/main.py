"""
AstroAI API 主应用

启动命令:
    uvicorn api.app.main:app --host 0.0.0.0 --port 8000 --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.app.api.v1 import classify

# 创建 FastAPI 应用
app = FastAPI(
    title="AstroAI-Core API",
    description="天文图像自动分类 API 服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(classify.router, prefix="/api/v1")


@app.get("/")
async def root():
    """API 根路径"""
    return {
        "service": "AstroAI-Core API",
        "version": "1.0.0",
        "description": "天文图像自动分类服务",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "AstroAI-Core"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
