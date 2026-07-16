from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1)
    rating: int | None = Field(None, ge=1, le=5)

class CommentResponse(BaseModel):
    id: int
    content: str
    rating: int | None
    escrito_id: int
    usuario_id: int
    usuario_name: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
