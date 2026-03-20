from pydantic import BaseModel
from datetime import datetime

class VersionBase(BaseModel):
    specification_id: int
    version_number: str
    file_path: str
    change_log: str
    is_current: int

class VersionCreate(VersionBase):
    pass

class VersionUpdate(BaseModel):
    version_number: str | None = None
    file_path: str | None = None
    change_log: str | None = None
    is_current: int | None = None

class VersionResponse(VersionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
