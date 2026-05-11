from typing import Optional, List

from pydantic import BaseModel, EmailStr

class UserRequestSchema(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponseSchema(BaseModel):
    id: int
    username: str
    email: EmailStr

class UpdateUserSchema(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class ListUserSchema(BaseModel):
    users: List[UserResponseSchema]