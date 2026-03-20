import asyncio
import random
import string
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
from app.db.base import Base
from app.models.user import User, Role, Permission
from app.models.specification import Specification, SpecVersion, SpecRelation

# 模拟规范标准数据
SPEC_TYPES = ["GB", "HB", "DB", "QB", "ISO"]
SPEC_LEVELS = [1, 2, 3]  # 1: 强制性, 2: 推荐性, 3: 指导性
SPEC_STATUS = [1, 2, 3]  # 1: 有效, 2: 修订中, 3: 待实施

# 规范标准名称和编号模板
SPEC_NAMES = [
    "建筑设计防火规范",
    "混凝土结构设计规范",
    "建筑抗震设计规范",
    "钢结构设计规范",
    "建筑地基基础设计规范",
    "建筑给水排水设计规范",
    "建筑电气设计规范",
    "建筑节能设计规范",
    "绿色建筑评价标准",
    "智能建筑设计标准"
]

# 编制单位
COMPILATION_UNITS = [
    "中华人民共和国住房和城乡建设部",
    "国家市场监督管理总局",
    "中国建筑科学研究院",
    "中国工程建设标准化协会",
    "住房和城乡建设部标准定额研究所"
]

# 关键词
KEYWORDS = [
    "建筑,设计,防火",
    "混凝土,结构,设计",
    "建筑,抗震,设计",
    "钢结构,设计,规范",
    "地基,基础,设计",
    "给水,排水,设计",
    "电气,设计,规范",
    "节能,设计,建筑",
    "绿色,建筑,评价",
    "智能,建筑,设计"
]

# 关联关系类型
RELATION_TYPES = ["reference", "supplement", "conflict"]

# 生成随机字符串
def generate_random_string(length=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

# 生成模拟PDF文件
def generate_mock_pdf(filename):
    """生成模拟PDF文件"""
    content = f"This is a mock PDF file for {filename}"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    return filename

# 上传文件到MinIO
async def upload_to_minio(client, bucket_name, file_path, object_name):
    """上传文件到MinIO"""
    try:
        # 检查存储桶是否存在
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
        
        # 上传文件
        client.fput_object(
            bucket_name,
            object_name,
            file_path,
            content_type="application/pdf"
        )
        print(f"✅ 上传文件 {object_name} 到MinIO成功")
        return f"/{bucket_name}/{object_name}"
    except S3Error as e:
        print(f"❌ 上传文件到MinIO失败: {e}")
        return None

# 生成测试数据
async def generate_test_data():
    """生成测试数据"""
    print("开始生成测试数据...")
    
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
            # 1. 生成规范标准数据
            print("\n1. 生成规范标准数据...")
            specs = []
            for i in range(10):
                spec_type = random.choice(SPEC_TYPES)
                spec_level = random.choice(SPEC_LEVELS)
                spec_status = random.choice(SPEC_STATUS)
                
                # 生成规范编号
                if spec_type == "GB":
                    code = f"GB {50000 + i + 16}-{2010 + i}"
                elif spec_type == "HB":
                    code = f"HB {random.randint(1000, 9999)}-{2010 + i}"
                elif spec_type == "DB":
                    code = f"DB {random.randint(1000, 9999)}-{2010 + i}"
                elif spec_type == "QB":
                    code = f"QB {random.randint(1000, 9999)}-{2010 + i}"
                else:  # ISO
                    code = f"ISO {random.randint(1000, 9999)}:{2010 + i}"
                
                # 生成文件名
                filename = f"spec_{code.replace(' ', '_').replace(':', '_')}.pdf"
                pdf_path = generate_mock_pdf(filename)
                
                # 上传到MinIO
                object_name = f"specs/{filename}"
                file_path = await upload_to_minio(minio_client, MINIO_BUCKET, pdf_path, object_name)
                
                # 清理本地文件
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
                
                # 创建规范标准
                spec = Specification(
                    name=SPEC_NAMES[i],
                    code=code,
                    type=spec_type,
                    level=spec_level,
                    status=spec_status,
                    compilation_unit=random.choice(COMPILATION_UNITS),
                    description=f"这是{SPEC_NAMES[i]}的详细描述，包含了相关的技术要求和规范。",
                    keywords=KEYWORDS[i],
                    file_path=file_path,
                    file_size=random.randint(1024, 1024000),  # 1KB-1MB
                    file_hash=generate_random_string(32),
                    version=f"{1 + i * 0.1:.1f}",
                    version_count=1,
                    view_count=random.randint(0, 1000),
                    download_count=random.randint(0, 500)
                )
                session.add(spec)
                specs.append(spec)
            
            await session.commit()
            print(f"✅ 生成了 {len(specs)} 条规范标准数据")
            
            # 2. 生成版本数据
            print("\n2. 生成版本数据...")
            versions = []
            for spec in specs:
                # 为每个规范生成1-3个版本
                version_count = random.randint(1, 3)
                for v in range(version_count):
                    version_number = f"{1 + v * 0.1:.1f}"
                    
                    # 生成版本文件名
                    version_filename = f"spec_{spec.code.replace(' ', '_').replace(':', '_')}_v{version_number.replace('.', '_')}.pdf"
                    version_pdf_path = generate_mock_pdf(version_filename)
                    
                    # 上传到MinIO
                    version_object_name = f"specs/versions/{version_filename}"
                    version_file_path = await upload_to_minio(minio_client, MINIO_BUCKET, version_pdf_path, version_object_name)
                    
                    # 清理本地文件
                    if os.path.exists(version_pdf_path):
                        os.remove(version_pdf_path)
                    
                    # 创建版本
                    version = SpecVersion(
                        specification_id=spec.id,
                        version_number=version_number,
                        file_path=version_file_path,
                        change_log=f"版本 {version_number} 的主要变更：{generate_random_string(20)}",
                        is_current=1 if v == version_count - 1 else 0
                    )
                    session.add(version)
                    versions.append(version)
            
            await session.commit()
            print(f"✅ 生成了 {len(versions)} 条版本数据")
            
            # 3. 生成关联关系数据
            print("\n3. 生成关联关系数据...")
            relations = []
            for i, spec in enumerate(specs):
                # 为每个规范生成1-2个关联关系
                relation_count = random.randint(1, 2)
                for _ in range(relation_count):
                    # 随机选择目标规范（不选自己）
                    target_index = random.choice([j for j in range(len(specs)) if j != i])
                    target_spec = specs[target_index]
                    
                    # 创建关联关系
                    relation = SpecRelation(
                        source_id=spec.id,
                        target_id=target_spec.id,
                        relation_type=random.choice(RELATION_TYPES),
                        description=f"{spec.name} 与 {target_spec.name} 的{RELATION_TYPES[0]}关系描述"
                    )
                    session.add(relation)
                    relations.append(relation)
            
            await session.commit()
            print(f"✅ 生成了 {len(relations)} 条关联关系数据")
            
            # 4. 测试Redis缓存
            print("\n4. 测试Redis缓存...")
            # 缓存规范标准数据
            for spec in specs:
                spec_data = {
                    "id": spec.id,
                    "name": spec.name,
                    "code": spec.code,
                    "type": spec.type,
                    "level": spec.level,
                    "status": spec.status,
                    "compilation_unit": spec.compilation_unit,
                    "description": spec.description,
                    "keywords": spec.keywords
                }
                redis_client.set(f"spec:{spec.id}", json.dumps(spec_data))
                print(f"✅ 缓存规范 {spec.code} 到Redis")
            
            # 缓存规范列表
            spec_list = []
            for spec in specs:
                spec_list.append({
                    "id": spec.id,
                    "name": spec.name,
                    "code": spec.code,
                    "type": spec.type
                })
            redis_client.set("specs:list", json.dumps(spec_list))
            print("✅ 缓存规范列表到Redis")
            
            # 验证缓存
            cached_spec = redis_client.get("specs:list")
            if cached_spec:
                print(f"✅ Redis缓存验证成功，规范列表长度: {len(json.loads(cached_spec))}")
            else:
                print("❌ Redis缓存验证失败")
            
            # 5. 验证数据
            print("\n5. 验证数据...")
            # 验证规范标准
            result = await session.execute(text("SELECT COUNT(*) FROM specifications"))
            spec_count = result.scalar()
            print(f"   规范标准数量: {spec_count}")
            
            # 验证版本
            result = await session.execute(text("SELECT COUNT(*) FROM spec_versions"))
            version_count = result.scalar()
            print(f"   版本数量: {version_count}")
            
            # 验证关联关系
            result = await session.execute(text("SELECT COUNT(*) FROM spec_relations"))
            relation_count = result.scalar()
            print(f"   关联关系数量: {relation_count}")
            
            print("\n🎉 测试数据生成完成！")
            print(f"\n生成统计：")
            print(f"- 规范标准: {spec_count} 条")
            print(f"- 版本: {version_count} 条")
            print(f"- 关联关系: {relation_count} 条")
            print(f"- 上传文件到MinIO: {len(specs) + len(versions)} 个")
            print(f"- 缓存到Redis: {spec_count + 1} 条数据")
            
    except Exception as e:
        print(f"生成测试数据时出错: {e}")
        raise
    finally:
        # 关闭引擎
        await engine.dispose()
        # 关闭Redis连接
        redis_client.close()


if __name__ == "__main__":
    asyncio.run(generate_test_data())
