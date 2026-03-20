import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from minio import Minio
from minio.error import S3Error
import redis
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取数据库URL
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+aiomysql://user:pass@localhost:3306/std_db")

# MinIO配置
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "standards")

# Redis配置
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6380/0")

# 导入模型
from app.models.specification import Specification, SpecVersion, SpecRelation

async def verify_test_data():
    """验证测试数据"""
    print("开始验证测试数据...")
    
    # 创建异步引擎
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    # 创建会话工厂
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    # 初始化MinIO客户端
    minio_client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )
    
    # 初始化Redis客户端
    redis_client = redis.from_url(REDIS_URL)
    
    try:
        async with async_session() as session:
            # 1. 验证MySQL数据
            print("\n1. 验证MySQL数据库数据:")
            
            # 验证规范标准
            result = await session.execute(text("SELECT COUNT(*) FROM specifications"))
            spec_count = result.scalar()
            print(f"   规范标准数量: {spec_count}")
            
            if spec_count > 0:
                # 查看前3条规范标准
                result = await session.execute(
                    text("SELECT id, name, code, type FROM specifications LIMIT 3")
                )
                specs = result.fetchall()
                print("   前3条规范标准:")
                for spec in specs:
                    print(f"     - {spec[2]}: {spec[1]} ({spec[3]})")
            
            # 验证版本
            result = await session.execute(text("SELECT COUNT(*) FROM spec_versions"))
            version_count = result.scalar()
            print(f"   版本数量: {version_count}")
            
            if version_count > 0:
                # 查看前3条版本
                result = await session.execute(
                    text("SELECT id, specification_id, version_number, is_current FROM spec_versions LIMIT 3")
                )
                versions = result.fetchall()
                print("   前3条版本:")
                for version in versions:
                    print(f"     - 规范ID: {version[1]}, 版本: {version[2]}, 当前版本: {version[3]}")
            
            # 验证关联关系
            result = await session.execute(text("SELECT COUNT(*) FROM spec_relations"))
            relation_count = result.scalar()
            print(f"   关联关系数量: {relation_count}")
            
            if relation_count > 0:
                # 查看前3条关联关系
                result = await session.execute(
                    text("SELECT id, source_id, target_id, relation_type FROM spec_relations LIMIT 3")
                )
                relations = result.fetchall()
                print("   前3条关联关系:")
                for relation in relations:
                    print(f"     - 源规范: {relation[1]} → 目标规范: {relation[2]} ({relation[3]})")
            
            # 2. 验证Redis缓存
            print("\n2. 验证Redis缓存:")
            
            # 验证规范列表缓存
            cached_specs = redis_client.get("specs:list")
            if cached_specs:
                spec_list = json.loads(cached_specs)
                print(f"   缓存的规范列表长度: {len(spec_list)}")
                print("   缓存的前3条规范:")
                for spec in spec_list[:3]:
                    print(f"     - {spec['code']}: {spec['name']} ({spec['type']})")
            else:
                print("   ❌ 规范列表缓存不存在")
            
            # 验证单个规范缓存
            if spec_count > 0:
                # 获取第一个规范的ID
                result = await session.execute(
                    text("SELECT id FROM specifications LIMIT 1")
                )
                spec_id = result.scalar()
                
                cached_spec = redis_client.get(f"spec:{spec_id}")
                if cached_spec:
                    spec_data = json.loads(cached_spec)
                    print(f"   缓存的规范详情 (ID: {spec_id}):")
                    print(f"     名称: {spec_data['name']}")
                    print(f"     编号: {spec_data['code']}")
                    print(f"     类型: {spec_data['type']}")
                else:
                    print(f"   ❌ 规范缓存不存在 (ID: {spec_id})")
            
            # 3. 验证MinIO存储
            print("\n3. 验证MinIO存储:")
            
            # 检查存储桶是否存在
            if minio_client.bucket_exists(MINIO_BUCKET):
                print(f"   ✅ 存储桶 {MINIO_BUCKET} 存在")
                
                # 列出前5个对象
                objects = minio_client.list_objects(MINIO_BUCKET, recursive=True)
                print("   前5个存储的文件:")
                count = 0
                for obj in objects:
                    if count < 5:
                        print(f"     - {obj.object_name} (大小: {obj.size} 字节)")
                        count += 1
                    else:
                        break
            else:
                print(f"   ❌ 存储桶 {MINIO_BUCKET} 不存在")
            
            # 4. 综合验证
            print("\n4. 综合验证结果:")
            all_passed = True
            
            if spec_count > 0:
                print("   ✅ 规范标准数据验证通过")
            else:
                print("   ❌ 规范标准数据验证失败")
                all_passed = False
            
            if version_count > 0:
                print("   ✅ 版本数据验证通过")
            else:
                print("   ❌ 版本数据验证失败")
                all_passed = False
            
            if relation_count > 0:
                print("   ✅ 关联关系数据验证通过")
            else:
                print("   ❌ 关联关系数据验证失败")
                all_passed = False
            
            if cached_specs:
                print("   ✅ Redis缓存验证通过")
            else:
                print("   ❌ Redis缓存验证失败")
                all_passed = False
            
            if minio_client.bucket_exists(MINIO_BUCKET):
                print("   ✅ MinIO存储验证通过")
            else:
                print("   ❌ MinIO存储验证失败")
                all_passed = False
            
            if all_passed:
                print("\n🎉 所有数据验证通过！测试环境搭建成功。")
            else:
                print("\n❌ 部分数据验证失败，需要检查。")
            
    except Exception as e:
        print(f"验证测试数据时出错: {e}")
        raise
    finally:
        # 关闭引擎
        await engine.dispose()
        # 关闭Redis连接
        redis_client.close()


if __name__ == "__main__":
    asyncio.run(verify_test_data())
