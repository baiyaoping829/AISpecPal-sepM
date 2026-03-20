from pydantic import BaseModel
from datetime import datetime

class RelationBase(BaseModel):
    source_id: int
    target_id: int
    relation_type: str
    description: str

class RelationCreate(RelationBase):
    pass

class RelationUpdate(BaseModel):
    source_id: int | None = None
    target_id: int | None = None
    relation_type: str | None = None
    description: str | None = None

class RelationResponse(RelationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
