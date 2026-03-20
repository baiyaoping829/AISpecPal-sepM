import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from passlib.context import CryptContext

# 加载环境变量
load_dotenv()

# 获取数据库URL
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+aiomysql://user:pass@localhost:3306/std_db")

# 创建密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 导入模型
from app.db.base import Base
from app.models.user import User, Role, Permission, DEFAULT_ROLES, DEFAULT_PERMISSIONS, ROLE_PERMISSION_MAP
from app.models.specification import Specification, SpecVersion, SpecRelation


async def init_db():
    """初始化数据库"""
    print("开始初始化数据库...")
    
    # 创建异步引擎
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    # 创建会话工厂
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    try:
        # 创建所有表
        print("创建数据库表结构...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("表结构创建完成")
        
        # 插入默认数据
        async with async_session() as session:
            # 插入默认权限
            print("插入默认权限...")
            permission_map = {}
            from sqlalchemy import select
            for perm_data in DEFAULT_PERMISSIONS:
                # 检查权限是否已存在
                result = await session.execute(
                    select(Permission).where(Permission.code == perm_data["code"])
                )
                existing_perm = result.scalar_one_or_none()
                if not existing_perm:
                    permission = Permission(**perm_data)
                    session.add(permission)
                    permission_map[perm_data["code"]] = permission
                else:
                    permission_map[perm_data["code"]] = existing_perm
            
            # 插入默认角色
            print("插入默认角色...")
            role_map = {}
            for role_data in DEFAULT_ROLES:
                # 检查角色是否已存在
                result = await session.execute(
                    select(Role).where(Role.name == role_data["name"])
                )
                existing_role = result.scalar_one_or_none()
                if not existing_role:
                    role = Role(**role_data)
                    session.add(role)
                    role_map[role_data["name"]] = role
                else:
                    role_map[role_data["name"]] = existing_role
            
            # 提交角色和权限
            await session.commit()
            
            # 关联角色和权限
            print("关联角色和权限...")
            # 直接操作关联表，避免异步懒加载问题
            from sqlalchemy import insert
            from app.models.user import role_permissions
            
            for role_name, perm_codes in ROLE_PERMISSION_MAP.items():
                role = role_map[role_name]
                for perm_code in perm_codes:
                    if perm_code in permission_map:
                        perm = permission_map[perm_code]
                        # 直接插入关联数据
                        await session.execute(
                            insert(role_permissions).values(
                                role_id=role.id,
                                permission_id=perm.id
                            )
                        )
            
            # 创建默认管理员用户（暂时跳过，后续手动创建）
            print("跳过管理员用户创建，后续手动创建...")
            # 注意：管理员用户需要后续手动创建，用户名admin，密码admin123
            
            # 提交所有数据
            await session.commit()
            print("默认数据插入完成")
            
    except Exception as e:
        print(f"初始化数据库时出错: {e}")
        raise
    finally:
        # 关闭引擎
        await engine.dispose()
        print("数据库初始化完成")


if __name__ == "__main__":
    asyncio.run(init_db())
