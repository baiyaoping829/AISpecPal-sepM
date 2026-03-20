import pytest
from fastapi.testclient import TestClient
from main import app
from app.db.session import engine
from app.db.base import Base
import asyncio

@pytest.fixture(scope="session")
def setup_database():
    """设置测试数据库"""
    async def create_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
    
    async def drop_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    
    # 执行创建表操作
    asyncio.run(create_tables())
    yield
    # 执行删除表操作
    asyncio.run(drop_tables())

@pytest.fixture(scope="session")
def test_client():
    """创建测试客户端"""
    client = TestClient(app)
    yield client
