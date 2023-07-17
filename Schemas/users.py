from typing import Optional
from datetime import datetime
from pydantic import UUID4, BaseModel, EmailStr, Field, validator


class UserCreate(BaseModel):
    """ Проверяет sign-up запрос """
    username: str
    email: EmailStr
    name: str
    password: str


class UserBase(BaseModel):
    """ Формирует тело ответа с деталями пользователя """
    email: EmailStr
    name: str
    username: str


class TokenBase(BaseModel):
    token: UUID4 = Field(..., alias="access_token")
    expires: datetime
    token_type: Optional[str] = "bearer"

    class Config:
        allow_population_by_field_name = True


class User(UserBase):
    """ Формирует тело ответа с деталями пользователя и токеном """
    token: TokenBase = {}


class TokenBaseOne(BaseModel):
    token: UUID4 = Field(..., alias="access_token")


class IdUser(UserBase):
    id: UUID4
