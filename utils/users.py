import hashlib
import random
import string
from datetime import datetime, timedelta
from fastapi import Response
from sqlalchemy.orm import Session
from uuid import uuid4
from modeling.models import Users, TokensTable
import shemas as user_schema


def get_random_string(length=12):
    """ Генерирует случайную строку, использующуюся как соль """
    return "".join(random.choice(string.ascii_letters) for _ in range(length))


def hash_password(password: str, salt: str = None):
    """ Хеширует пароль с солью """
    if salt is None:
        salt = get_random_string()
    enc = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return enc.hex()


def validate_password(password: str, hashed_password: str):
    """ Проверяет, что хеш пароля совпадает с хешем из БД """
    salt, hashed = hashed_password.split("$")
    return hash_password(password, salt) == hashed


async def get_user_by_email(email: str, db: Session):
    """ Возвращает информацию о пользователе по email """
    db_user = db.query(Users).filter(Users.email == email).first()
    return db_user


async def check_user_by_email(email: str, username: str, db: Session):
    """ проверяет есть  ли такие email и username уже в БД """
    db_email = db.query(Users).filter(Users.email == email).first()
    db_username = db.query(Users).filter(Users.username == username).first()
    if db_email or db_username:
        return True
    return False


async def make_user_is_active(email: str, db: Session):
    """ Устанавливает, что пользователь активный """
    db_user = db.query(Users).filter(Users.email == email).first()
    db_user.is_active = True
    db.commit()
    db.refresh(db_user)
    return True


async def get_user_by_token(token: str, db: Session):
    """ Возвращает информацию о владельце указанного токена """
    db_user = db.query(TokensTable, Users).with_entities(Users.username, Users.name, Users.email,
                                                         Users.is_active).filter(
        TokensTable.token == token, TokensTable.expires > datetime.now()).filter(TokensTable.user == Users.id).first()
    return db_user


async def get_user_by_token_(token: str, db: Session):
    """ Возвращает информацию о владельце указанного токена другие поля """
    db_user = db.query(Users, TokensTable).with_entities(Users.id, Users.username, Users.name, Users.email,
                                                         Users.is_active).filter(
                                                            TokensTable.token == token,
                                                            TokensTable.expires > datetime.now()
                                                            ).filter(
        TokensTable.user == Users.id).first()
    return db_user


async def create_user_token(user_id: str, db: Session):
    """ Создает токен для пользователя с указанным user_id """
    user_token = db.query(TokensTable).filter(TokensTable.user == user_id).first()
    if user_token and user_token.expires > datetime.now():
        new_token = user_token
    else:
        new_token = TokensTable(expires=(datetime.now() + timedelta(weeks=2)), user=user_id, token=uuid4().hex)
        db.add(new_token)
        db.commit()
        db.refresh(new_token)
    token_dict = {"token": str(new_token.token), "expires": new_token.expires}
    return token_dict


async def create_user(user: user_schema.UserCreate, db: Session):
    """ Создает нового пользователя в БД """
    salt = get_random_string()
    hashed_password = hash_password(user.password, salt)
    new_user = Users(email=user.email, name=user.name, password=f"{salt}${hashed_password}", username=user.username)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    user_id = new_user.id
    token = await create_user_token(user_id, db)
    token_dict = {"token": token['token'], "expires": token['expires']}
    return {**user.dict(), "id": user_id, "is_created": True, "token": token_dict}


async def create_cookie(response: Response, token_user):
    """ Установка токена в cookie """
    response.set_cookie(
        key='bearer',
        value=token_user['token'],
        expires=token_user['expires'],
        httponly=True)
    return response


async def set_user_is_active(email: str, db: Session):
    """ При логине установка активация пользователя """
    db_user = db.query(Users).filter(Users.email == email).first()
    db_user.is_active = True
    db.commit()
    db.refresh(db_user)
    return


async def get_users(db: Session):
    """ Получение информации о всех пользователях """
    db_users = db.query(Users).with_entities(Users.username, Users.name, Users.email, Users.is_active).all()
    return db_users
