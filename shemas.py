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

    class Config:
        allow_population_by_field_name = True

    @validator("token")
    def hexlify_token(cls, value):
        """ Конвертирует UUID в hex строку """
        return value.hex


class User(UserBase):
    """ Формирует тело ответа с деталями пользователя и токеном """
    token: TokenBase = {}


class UserLogin(BaseModel):
    """ Проверяет sign-up запрос """
    email: EmailStr
    username: str
    password: str


class TokenBaseOne(BaseModel):
    token: UUID4 = Field(..., alias="access_token")

    class Config:
        allow_population_by_field_name = True

    @validator("token")
    def hexlify_token(cls, value):
        """ Конвертирует UUID в hex строку """
        return value.hex


class TokenOne(UserBase):
    """ Формирует тело ответа с деталями пользователя """
    token: TokenBaseOne = {}



