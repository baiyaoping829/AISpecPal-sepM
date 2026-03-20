from pydantic import BaseModel
from datetime import datetime

class SpecificationBase(BaseModel):
    name: str
    code: str
    type: str
    level: int
    status: int
    compilation_unit: str
    description: str
    keywords: str

class SpecificationCreate(SpecificationBase):
    file_path: str
    file_size: int
    file_hash: str

class SpecificationUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    type: str | None = None
    level: int | None = None
    status: int | None = None
    compilation_unit: str | None = None
    description: str | None = None
    keywords: str | None = None

class SpecificationResponse(SpecificationBase):
    id: int
    file_path: str
    file_size: int
    file_hash: str
    version: str
    version_count: int
    view_count: int
    download_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
