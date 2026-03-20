from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.api.schemas.specification import SpecificationCreate, SpecificationUpdate, SpecificationResponse
from app.api.deps import get_current_user
from app.models.specification import Specification
from app.api.cache import CacheManager, CACHE_PREFIX
import json

router = APIRouter()

@router.get("/")
async def get_specifications(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取规范标准列表"""
    # 尝试从缓存中获取
    cache_key = f"{CACHE_PREFIX['spec_list']}:{skip}:{limit}"
    cached_specs = CacheManager.get(cache_key)
    if cached_specs:
        return cached_specs
    
    # 从数据库中获取
    result = await db.execute(select(Specification).offset(skip).limit(limit))
    specifications = result.scalars().all()
    
    # 转换为可序列化的格式
    specs_data = []
    for spec in specifications:
        specs_data.append({
            "id": spec.id,
            "name": spec.name,
            "code": spec.code,
            "type": spec.type,
            "level": spec.level,
            "status": spec.status,
            "compilation_unit": spec.compilation_unit,
            "description": spec.description,
            "keywords": spec.keywords,
            "file_path": spec.file_path,
            "file_size": spec.file_size,
            "file_hash": spec.file_hash,
            "version": spec.version,
            "version_count": spec.version_count,
            "view_count": spec.view_count,
            "download_count": spec.download_count,
            "created_at": spec.created_at.isoformat() if spec.created_at else None,
            "updated_at": spec.updated_at.isoformat() if spec.updated_at else None
        })
    
    # 缓存结果
    CacheManager.set(cache_key, specs_data, expire=3600)
    
    return specifications

@router.get("/{spec_id}", response_model=SpecificationResponse)
async def get_specification(
    spec_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取规范标准详情"""
    # 尝试从缓存中获取
    cache_key = f"{CACHE_PREFIX['spec']}{spec_id}"
    cached_spec = CacheManager.get(cache_key)
    if cached_spec:
        return cached_spec
    
    # 从数据库中获取
    specification = await db.get(Specification, spec_id)
    if not specification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specification not found"
        )
    
    # 转换为可序列化的格式
    spec_data = {
        "id": specification.id,
        "name": specification.name,
        "code": specification.code,
        "type": specification.type,
        "level": specification.level,
        "status": specification.status,
        "compilation_unit": specification.compilation_unit,
        "description": specification.description,
        "keywords": specification.keywords,
        "file_path": specification.file_path,
        "file_size": specification.file_size,
        "file_hash": specification.file_hash,
        "version": specification.version,
        "version_count": specification.version_count,
        "view_count": specification.view_count,
        "download_count": specification.download_count,
        "created_at": specification.created_at.isoformat() if specification.created_at else None,
        "updated_at": specification.updated_at.isoformat() if specification.updated_at else None
    }
    
    # 缓存结果
    CacheManager.set(cache_key, spec_data, expire=3600)
    
    return specification

@router.post("/", response_model=SpecificationResponse)
async def create_specification(
    spec_data: SpecificationCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建规范标准"""
    # 检查规范编号是否已存在
    result = await db.execute(select(Specification).where(Specification.code == spec_data.code))
    existing_spec = result.scalar_one_or_none()
    if existing_spec:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specification code already exists"
        )
    
    # 创建新规范标准
    new_spec = Specification(
        name=spec_data.name,
        code=spec_data.code,
        type=spec_data.type,
        level=spec_data.level,
        status=spec_data.status,
        compilation_unit=spec_data.compilation_unit,
        description=spec_data.description,
        keywords=spec_data.keywords,
        file_path=spec_data.file_path,
        file_size=spec_data.file_size,
        file_hash=spec_data.file_hash,
        version="1.0",
        version_count=1,
        view_count=0,
        download_count=0
    )
    
    db.add(new_spec)
    await db.commit()
    await db.refresh(new_spec)
    
    # 清除规范标准列表缓存
    CacheManager.delete_pattern(f"{CACHE_PREFIX['spec_list']}*")
    
    return new_spec

@router.put("/{spec_id}", response_model=SpecificationResponse)
async def update_specification(
    spec_id: int,
    spec_data: SpecificationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新规范标准"""
    specification = await db.get(Specification, spec_id)
    if not specification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specification not found"
        )
    
    # 更新规范标准
    update_data = spec_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(specification, field, value)
    
    await db.commit()
    await db.refresh(specification)
    
    # 清除相关缓存
    CacheManager.delete(f"{CACHE_PREFIX['spec']}{spec_id}")
    CacheManager.delete_pattern(f"{CACHE_PREFIX['spec_list']}*")
    
    return specification

@router.delete("/{spec_id}")
async def delete_specification(
    spec_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """删除规范标准"""
    specification = await db.get(Specification, spec_id)
    if not specification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specification not found"
        )
    
    await db.delete(specification)
    await db.commit()
    
    # 清除相关缓存
    CacheManager.delete(f"{CACHE_PREFIX['spec']}{spec_id}")
    CacheManager.delete_pattern(f"{CACHE_PREFIX['spec_list']}*")
    
    return {"message": "Specification deleted successfully"}
