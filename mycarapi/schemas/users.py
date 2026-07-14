from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, EmailStr

class UserRequestSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)     # permite a criação dessa classe a partir de objetos diferentes de um dict
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime


class UpdateUserSchema(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class ListUserSchema(BaseModel):
    users: List[UserResponseSchema]
    offset: int
    limit: int