from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

class UserRequestSchema(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator('username')
    def username_min_length(cls, uname):
        if len(uname) <= 3:
            raise ValueError('Username deve possuir mais que 3 caracteres')
        return uname

    @field_validator('password')
    def username_min_length(cls, pwrd):
        if len(pwrd) < 8:      # Verificação mínima de senha
            raise ValueError('Senha deve possuir pelo menos 8 caracteres')
        return pwrd

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

    @field_validator('username')
    def username_min_length(cls, uname):
        if len(uname) <= 3:
            raise ValueError('Username deve possuir mais que 3 caracteres')
        return uname

    @field_validator('password')
    def username_min_length(cls, pwrd):
        if len(pwrd) < 8:      # Verificação mínima de senha
            raise ValueError('Senha deve possuir pelo menos 8 caracteres')
        return pwrd


class ListUserSchema(BaseModel):
    users: List[UserResponseSchema]
    offset: int
    limit: int