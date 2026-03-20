from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

from app.db.base import Base


# 用户-角色关联表
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True)
)


# 角色-权限关联表
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True)
)


class UserStatus(str, PyEnum):
    ACTIVE = "active"
    DISABLED = "disabled"
    PENDING = "pending"


class UserLevel(int, PyEnum):
    FREE = 0       # 免费用户
    BASIC = 1      # 普通会员
    PREMIUM = 2    # 高级会员
    ENTERPRISE = 3 # 企业用户


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    wechat = Column(String(100), nullable=True)
    
    # 认证相关
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # 等级和状态
    user_level = Column(Integer, default=0, comment="用户等级")
    status = Column(String(20), default="active", comment="用户状态")
    
    # 审计字段
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # 关系
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    
    @property
    def permissions(self):
        """获取用户所有权限"""
        perms = set()
        for role in self.roles:
            for perm in role.permissions:
                perms.add(perm.code)
        return list(perms)
    
    def has_permission(self, permission_code: str) -> bool:
        """检查是否有指定权限"""
        if self.is_superuser:
            return True
        return permission_code in self.permissions
    
    def __repr__(self):
        return f"<User {self.username}>"


class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, comment="角色名称")
    description = Column(String(500), nullable=True, comment="角色描述")
    is_system = Column(Boolean, default=False, comment="是否为系统角色")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    
    def __repr__(self):
        return f"<Role {self.name}>"


class Permission(Base):
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), unique=True, nullable=False, comment="权限代码")
    name = Column(String(100), nullable=False, comment="权限名称")
    description = Column(String(500), nullable=True, comment="权限描述")
    module = Column(String(50), nullable=False, comment="所属模块")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")
    
    def __repr__(self):
        return f"<Permission {self.code}>"


# 初始化数据
DEFAULT_ROLES = [
    {"name": "admin", "description": "管理员", "is_system": True},
    {"name": "editor", "description": "编辑者", "is_system": True},
    {"name": "viewer", "description": "查看者", "is_system": True},
    {"name": "auditor", "description": "审计员", "is_system": True},
]

DEFAULT_PERMISSIONS = [
    # 规范标准权限
    {"code": "spec:read", "name": "查看规范", "module": "spec"},
    {"code": "spec:create", "name": "创建规范", "module": "spec"},
    {"code": "spec:update", "name": "编辑规范", "module": "spec"},
    {"code": "spec:delete", "name": "删除规范", "module": "spec"},
    {"code": "spec:export", "name": "导出规范", "module": "spec"},
    
    # 文档权限
    {"code": "document:upload", "name": "上传文档", "module": "document"},
    {"code": "document:download", "name": "下载文档", "module": "document"},
    {"code": "document:preview", "name": "预览文档", "module": "document"},
    {"code": "document:delete", "name": "删除文档", "module": "document"},
    
    # 版本权限
    {"code": "version:read", "name": "查看版本", "module": "version"},
    {"code": "version:create", "name": "创建版本", "module": "version"},
    {"code": "version:rollback", "name": "回滚版本", "module": "version"},
    
    # 用户权限
    {"code": "user:read", "name": "查看用户", "module": "user"},
    {"code": "user:create", "name": "创建用户", "module": "user"},
    {"code": "user:update", "name": "编辑用户", "module": "user"},
    {"code": "user:delete", "name": "删除用户", "module": "user"},
    
    # 角色权限
    {"code": "role:read", "name": "查看角色", "module": "role"},
    {"code": "role:create", "name": "创建角色", "module": "role"},
    {"code": "role:update", "name": "编辑角色", "module": "role"},
    {"code": "role:delete", "name": "删除角色", "module": "role"},
    
    # 系统权限
    {"code": "system:config", "name": "系统配置", "module": "system"},
    {"code": "system:log", "name": "查看日志", "module": "system"},
]

# 角色-权限映射
ROLE_PERMISSION_MAP = {
    "admin": [p["code"] for p in DEFAULT_PERMISSIONS],  # 全部权限
    "editor": [
        "spec:read", "spec:create", "spec:update",
        "document:upload", "document:download", "document:preview",
        "version:read", "version:create"
    ],
    "viewer": [
        "spec:read", "document:download", "document:preview", "version:read"
    ],
    "auditor": [
        "spec:read", "document:download", "document:preview", 
        "version:read", "system:log"
    ],
}
