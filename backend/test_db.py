import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取数据库URL
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+aiomysql://user:pass@localhost:3306/std_db")

# 导入模型
from app.db.base import Base
from app.models.user import User, Role, Permission
from app.models.specification import Specification


async def test_db():
    """测试数据库初始化"""
    print("开始测试数据库初始化...")
    
    # 创建异步引擎
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    # 创建会话工厂
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    try:
        async with async_session() as session:
            # 测试权限数据
            print("\n1. 测试权限数据:")
            result = await session.execute(text("SELECT COUNT(*) FROM permissions"))
            perm_count = result.scalar()
            print(f"   权限数量: {perm_count}")
            if perm_count > 0:
                print("   ✅ 权限数据初始化成功")
            else:
                print("   ❌ 权限数据初始化失败")
            
            # 测试角色数据
            print("\n2. 测试角色数据:")
            result = await session.execute(text("SELECT COUNT(*) FROM roles"))
            role_count = result.scalar()
            print(f"   角色数量: {role_count}")
            if role_count > 0:
                print("   ✅ 角色数据初始化成功")
            else:
                print("   ❌ 角色数据初始化失败")
            
            # 测试角色权限关联
            print("\n3. 测试角色权限关联:")
            result = await session.execute(text("SELECT COUNT(*) FROM role_permissions"))
            relation_count = result.scalar()
            print(f"   角色权限关联数量: {relation_count}")
            if relation_count > 0:
                print("   ✅ 角色权限关联初始化成功")
            else:
                print("   ❌ 角色权限关联初始化失败")
            
            # 测试规范标准表
            print("\n4. 测试规范标准表:")
            result = await session.execute(text("SELECT COUNT(*) FROM specifications"))
            spec_count = result.scalar()
            print(f"   规范标准数量: {spec_count}")
            print("   ✅ 规范标准表创建成功")
            
            # 测试版本表
            print("\n5. 测试版本表:")
            result = await session.execute(text("SELECT COUNT(*) FROM spec_versions"))
            version_count = result.scalar()
            print(f"   版本数量: {version_count}")
            print("   ✅ 版本表创建成功")
            
            # 测试关联关系表
            print("\n6. 测试关联关系表:")
            result = await session.execute(text("SELECT COUNT(*) FROM spec_relations"))
            relation_count = result.scalar()
            print(f"   关联关系数量: {relation_count}")
            print("   ✅ 关联关系表创建成功")
            
            print("\n🎉 数据库初始化测试完成！")
            print("\n注意：管理员用户需要后续手动创建，用户名admin，密码admin123")
            
    except Exception as e:
        print(f"测试过程中出错: {e}")
        raise
    finally:
        # 关闭引擎
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_db())
