from pydantic import BaseModel, Field
from decimal import Decimal

class ServiceCreate(BaseModel):
    name: str=Field(min_length=1, max_length=100)

class ServiceRead(BaseModel):
    service_id: int
    name: str

class ServiceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)

class ParentCreate(BaseModel):
    name: str=Field(min_length=1, max_length=100)
    contact: str=Field(min_length=1, max_length=100)

class StudentCreate(BaseModel):
    name: str=Field(min_length=1, max_length=100)
    contact: str | None =Field(default=None, max_length=100)
    service_id: int
    cost_per_hour: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    parent_id: int | None = None
    parent: ParentCreate | None = None

class StudentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    contact: str | None = Field(default=None, max_length=100)
    service_id: int | None = None
    cost_per_hour: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    parent_id: int | None = None

class StudentRead(BaseModel):
    student_id: int
    name: str
    contact: str | None
    parent_id: int | None
    service_id: int
    cost_per_hour: Decimal
    is_active: bool
