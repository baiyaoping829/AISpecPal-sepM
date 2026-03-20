from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.db.session import get_db
from app.api.schemas.version import VersionCreate, VersionUpdate, VersionResponse
from app.api.deps import get_current_user
from app.models.specification import SpecVersion, Specification

router = APIRouter()

@router.get("/specification/{spec_id}")
async def get_versions_by_specification(
    spec_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取指定规范标准的所有版本"""
    # 检查规范标准是否存在
    specification = await db.get(Specification, spec_id)
    if not specification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specification not found"
        )
    
    # 获取所有版本
    result = await db.execute(select(SpecVersion).where(SpecVersion.specification_id == spec_id))
    versions = result.scalars().all()
    return versions

@router.get("/{version_id}", response_model=VersionResponse)
async def get_version(
    version_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取版本详情"""
    version = await db.get(SpecVersion, version_id)
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found"
        )
    return version

@router.post("/", response_model=VersionResponse)
async def create_version(
    version_data: VersionCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建版本"""
    # 检查规范标准是否存在
    specification = await db.get(Specification, version_data.specification_id)
    if not specification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specification not found"
        )
    
    # 如果是当前版本，将其他版本设置为非当前版本
    if version_data.is_current == 1:
        await db.execute(
            update(SpecVersion)
            .where(SpecVersion.specification_id == version_data.specification_id)
            .values(is_current=0)
        )
    
    # 创建新版本
    new_version = SpecVersion(
        specification_id=version_data.specification_id,
        version_number=version_data.version_number,
        file_path=version_data.file_path,
        change_log=version_data.change_log,
        is_current=version_data.is_current
    )
    
    db.add(new_version)
    await db.commit()
    await db.refresh(new_version)
    
    # 更新规范标准的版本信息
    if version_data.is_current == 1:
        specification.version = version_data.version_number
        specification.version_count += 1
        await db.commit()
    
    return new_version

@router.put("/{version_id}", response_model=VersionResponse)
async def update_version(
    version_id: int,
    version_data: VersionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新版本"""
    version = await db.get(SpecVersion, version_id)
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found"
        )
    
    # 如果设置为当前版本，将其他版本设置为非当前版本
    if version_data.is_current == 1:
        await db.execute(
            update(SpecVersion)
            .where(SpecVersion.specification_id == version.specification_id)
            .values(is_current=0)
        )
    
    # 更新版本
    update_data = version_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(version, field, value)
    
    await db.commit()
    await db.refresh(version)
    
    # 更新规范标准的版本信息
    if version_data.is_current == 1:
        specification = await db.get(Specification, version.specification_id)
        specification.version = version.version_number
        await db.commit()
    
    return version

@router.delete("/{version_id}")
async def delete_version(
    version_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """删除版本"""
    version = await db.get(SpecVersion, version_id)
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found"
        )
    
    # 检查是否是当前版本
    if version.is_current == 1:
        # 查找其他版本
        result = await db.execute(
            select(SpecVersion)
            .where(SpecVersion.specification_id == version.specification_id)
            .where(SpecVersion.id != version_id)
            .order_by(SpecVersion.id.desc())
        )
        other_version = result.scalar_one_or_none()
        
        # 如果有其他版本，设置为当前版本
        if other_version:
            other_version.is_current = 1
            specification = await db.get(Specification, version.specification_id)
            specification.version = other_version.version_number
    
    await db.delete(version)
    await db.commit()
    
    return {"message": "Version deleted successfully"}
