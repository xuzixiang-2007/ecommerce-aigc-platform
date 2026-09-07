"""FastAPI 入口 - 启动后端服务"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routers import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化数据库"""
    await init_db()
    print(f"[{settings.APP_NAME}] 数据库初始化完成")
    yield
    print("服务关闭")


app = FastAPI(
    title=settings.APP_NAME,
    description="电商AIGC商品图合规溯源存证平台 API",
    version="1.0.0",
    lifespan=lifespan,
)

# 跨域配置（允许前端访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发阶段允许所有来源，生产环境需限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router)


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "docs": "/docs",  # Swagger UI
        "status": "running",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


# 启动命令：uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
