from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class WritingBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    status: str = Field("borrador", pattern="^(borrador|publicado)$")
    tags: list[str] = Field(default_factory=list)

class WritingCreate(WritingBase):
    pass

class WritingUpdate(WritingBase):
    pass

class WritingResponse(BaseModel):
    id: int
    title: str
    content: str
    status: str
    tags: list[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
