from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator


class BrandRequestSchema(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True

    @field_validator('name')
    def validate_name(cls, name):
        if len(name.strip()) < 3:
            raise ValueError("Nome da marca deve possuir mais de 2 caracteres")
        return name.strip()

class BrandResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

class BrandUpdateSchema(BaseModel):
    name: Optional[str]
    description: Optional[str]
    is_active: Optional[bool]

    @field_validator('name')
    def validate_name(cls, name):
        if len(name) <= 3:
            raise ValueError("Nome da marca não pode ter 3 dígitos ou menos")
        return name

class BrandListSchema(BaseModel):
    brands: List[BrandResponseSchema]
    offset: int
    limit: int