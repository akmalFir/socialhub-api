from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PostCreate(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    content: str = Field(min_length=1, max_length=2000)


class PostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    content: str
    created_at: datetime
