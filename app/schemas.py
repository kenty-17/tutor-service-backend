from pydantic import BaseModel, Field

class ServiceCreate(BaseModel):
    name: str=Field(min_length=1, max_length=100)

class ServiceRead(BaseModel):
    id: int
    name: str

class ServiceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
