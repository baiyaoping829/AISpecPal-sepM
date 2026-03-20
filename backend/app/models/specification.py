from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

from app.db.base import Base


class SpecType(str, PyEnum):
    GB = "GB"      # 国家标准
    HB = "HB"      # 行业标准
    DB = "DB"      # 地方标准
    QB = "QB"      # 企业标准
    ISO = "ISO"    # 国际标准


class SpecLevel(int, PyEnum):
    MANDATORY = 1      # 强制性标准
    RECOMMENDED = 2    # 推荐性标准
    GUIDANCE = 3       # 指导性标准


class SpecStatus(int, PyEnum):
    ABOLISHED = 0      # 废止
    ACTIVE = 1         # 有效
    REVISING = 2       # 修订中
    PENDING = 3        # 待实施


class Specification(Base):
    __tablename__ = "specifications"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(500), nullable=False, index=True, comment="规范名称")
    code = Column(String(100), unique=True, nullable=False, index=True, comment="规范编号")
    type = Column(String(10), nullable=False, comment="规范类型")
    level = Column(Integer, nullable=False, comment="规范等级")
    status = Column(Integer, default=1, comment="状态")
    
    # 时间相关
    implementation_date = Column(Date, nullable=True, comment="实施日期")
    abolition_date = Column(Date, nullable=True, comment="废止日期")
    
    # 内容相关
    compilation_unit = Column(String(500), nullable=True, comment="编制单位")
    description = Column(Text, nullable=True, comment="规范描述")
    keywords = Column(String(500), nullable=True, comment="关键词")
    
    # 文件相关
    file_path = Column(String(500), nullable=True, comment="PDF文件路径")
    file_size = Column(Integer, nullable=True, comment="文件大小")
    file_hash = Column(String(64), nullable=True, comment="文件哈希")
    
    # 版本相关
    version = Column(String(50), default="1.0", comment="版本号")
    version_count = Column(Integer, default=1, comment="版本数量")
    
    # 统计相关
    view_count = Column(Integer, default=0, comment="浏览次数")
    download_count = Column(Integer, default=0, comment="下载次数")
    
    # 审计字段
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # 关系
    versions = relationship("SpecVersion", back_populates="specification", cascade="all, delete-orphan")
    source_relations = relationship("SpecRelation", foreign_keys="SpecRelation.source_id", back_populates="source_spec")
    target_relations = relationship("SpecRelation", foreign_keys="SpecRelation.target_id", back_populates="target_spec")
    
    def __repr__(self):
        return f"<Specification {self.code}: {self.name}>"


class SpecVersion(Base):
    __tablename__ = "spec_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    specification_id = Column(Integer, ForeignKey("specifications.id"), nullable=False)
    version_number = Column(String(50), nullable=False, comment="版本号")
    file_path = Column(String(500), nullable=True, comment="PDF文件路径")
    change_log = Column(Text, nullable=True, comment="变更说明")
    is_current = Column(Integer, default=0, comment="是否为当前版本")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # 关系
    specification = relationship("Specification", back_populates="versions")
    
    def __repr__(self):
        return f"<SpecVersion {self.version_number} for {self.specification_id}>"


class SpecRelation(Base):
    __tablename__ = "spec_relations"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("specifications.id"), nullable=False, comment="源规范")
    target_id = Column(Integer, ForeignKey("specifications.id"), nullable=False, comment="目标规范")
    relation_type = Column(String(50), nullable=False, comment="关系类型")  # reference/supplement/conflict
    description = Column(Text, nullable=True, comment="关系描述")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    source_spec = relationship("Specification", foreign_keys=[source_id], back_populates="source_relations")
    target_spec = relationship("Specification", foreign_keys=[target_id], back_populates="target_relations")
    
    def __repr__(self):
        return f"<SpecRelation {self.source_id} -> {self.target_id}: {self.relation_type}>"
