from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.api.schemas.relation import RelationCreate, RelationUpdate, RelationResponse
from app.api.deps import get_current_user
from app.models.specification import SpecRelation, Specification

router = APIRouter()

@router.get("/source/{spec_id}")
async def get_relations_by_source(
    spec_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取指定规范标准作为源的所有关联关系"""
    # 检查规范标准是否存在
    specification = await db.get(Specification, spec_id)
    if not specification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specification not found"
        )
    
    # 获取所有关联关系
    result = await db.execute(select(SpecRelation).where(SpecRelation.source_id == spec_id))
    relations = result.scalars().all()
    return relations

@router.get("/target/{spec_id}")
async def get_relations_by_target(
    spec_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取指定规范标准作为目标的所有关联关系"""
    # 检查规范标准是否存在
    specification = await db.get(Specification, spec_id)
    if not specification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specification not found"
        )
    
    # 获取所有关联关系
    result = await db.execute(select(SpecRelation).where(SpecRelation.target_id == spec_id))
    relations = result.scalars().all()
    return relations

@router.get("/{relation_id}", response_model=RelationResponse)
async def get_relation(
    relation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取关联关系详情"""
    relation = await db.get(SpecRelation, relation_id)
    if not relation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relation not found"
        )
    return relation

@router.post("/", response_model=RelationResponse)
async def create_relation(
    relation_data: RelationCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建关联关系"""
    # 检查源规范标准是否存在
    source_spec = await db.get(Specification, relation_data.source_id)
    if not source_spec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source specification not found"
        )
    
    # 检查目标规范标准是否存在
    target_spec = await db.get(Specification, relation_data.target_id)
    if not target_spec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target specification not found"
        )
    
    # 检查是否已经存在相同的关联关系
    result = await db.execute(
        select(SpecRelation)
        .where(SpecRelation.source_id == relation_data.source_id)
        .where(SpecRelation.target_id == relation_data.target_id)
    )
    existing_relation = result.scalar_one_or_none()
    if existing_relation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Relation already exists"
        )
    
    # 创建新关联关系
    new_relation = SpecRelation(
        source_id=relation_data.source_id,
        target_id=relation_data.target_id,
        relation_type=relation_data.relation_type,
        description=relation_data.description
    )
    
    db.add(new_relation)
    await db.commit()
    await db.refresh(new_relation)
    
    return new_relation

@router.put("/{relation_id}", response_model=RelationResponse)
async def update_relation(
    relation_id: int,
    relation_data: RelationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新关联关系"""
    relation = await db.get(SpecRelation, relation_id)
    if not relation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relation not found"
        )
    
    # 如果更新了源或目标规范标准，检查它们是否存在
    if relation_data.source_id is not None:
        source_spec = await db.get(Specification, relation_data.source_id)
        if not source_spec:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source specification not found"
            )
    
    if relation_data.target_id is not None:
        target_spec = await db.get(Specification, relation_data.target_id)
        if not target_spec:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target specification not found"
            )
    
    # 检查是否已经存在相同的关联关系
    if relation_data.source_id is not None and relation_data.target_id is not None:
        result = await db.execute(
            select(SpecRelation)
            .where(SpecRelation.source_id == relation_data.source_id)
            .where(SpecRelation.target_id == relation_data.target_id)
            .where(SpecRelation.id != relation_id)
        )
        existing_relation = result.scalar_one_or_none()
        if existing_relation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Relation already exists"
            )
    
    # 更新关联关系
    update_data = relation_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(relation, field, value)
    
    await db.commit()
    await db.refresh(relation)
    
    return relation

@router.delete("/{relation_id}")
async def delete_relation(
    relation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """删除关联关系"""
    relation = await db.get(SpecRelation, relation_id)
    if not relation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relation not found"
        )
    
    await db.delete(relation)
    await db.commit()
    
    return {"message": "Relation deleted successfully"}
