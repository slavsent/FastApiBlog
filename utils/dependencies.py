from utils import users as users_utils
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from modeling.models import Users
from core.db import get_db


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login/")


async def get_current_user_(access_token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """ Получение данных о пользователе по авторизационному токену"""
    user = await users_utils.get_user_by_token_(access_token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return user


async def get_current_user(token, db: Session):
    """ Получение информации о пользователе по токену в адресе """
    user = await users_utils.get_user_by_token(token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_users(token, db: Session):
    """ Получение информации о всех пользователях по токену в адресе """
    user = await users_utils.get_user_by_token(token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    db_users = db.query(Users).with_entities(Users.username, Users.name, Users.email, Users.is_active).all()
    return db_users


async def get_current_user_from_cookie(request: Request, db: Session = Depends(get_db)):
    """
    Получение пользователя по токену из cookie
    """
    token = request.cookies.get("bearer")
    user = await users_utils.get_user_by_token_(token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return user
