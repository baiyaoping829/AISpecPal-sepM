from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import api_router
from app.db.session import engine
from app.db.base import Base
import asyncio

app = FastAPI(
    title="AISpecPal API",
    description="工程规范标准管理系统API",
    version="0.1.0"
)

# 创建数据库表
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# 启动时创建表
@app.on_event("startup")
async def startup_event():
    await create_tables()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含API路由
app.include_router(api_router)

# 根路径
@app.get("/")
async def root():
    return {"message": "Welcome to AISpecPal API"}

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
