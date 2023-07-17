import Schemas.users as users
from utils import users as users_utils
from utils.dependencies import get_current_user, get_users, get_current_user_
from fastapi import APIRouter, Depends, HTTPException, Form, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse, JSONResponse
import starlette.status as status
from fastapi.security import OAuth2PasswordBearer
from core.db import get_db
from typing import List


router = APIRouter()


@router.post("/", response_class=RedirectResponse)
async def auth(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Обработка логина для frontend
    """
    user = await users_utils.get_user_by_email(form_data.username, db)

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email")

    if not users_utils.validate_password(
            password=form_data.password, hashed_password=user.password
    ):
        raise HTTPException(status_code=400, detail="Incorrect password")
    token_user = await users_utils.create_user_token(user.id, db)
    response = RedirectResponse(f"/users/", status_code=status.HTTP_302_FOUND)
    try:
        response.set_cookie(
            key='bearer',
            value=token_user['token'],
            expires=token_user['expires'],
            httponly=True)
    except Exception:
        print('err')
        raise HTTPException(status_code=400, detail="Don't set token in cookie")
    await users_utils.set_user_is_active(form_data.username, db)
    return response


@router.post("/api/login/", response_model=users.TokenBase)
async def auth_api(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """ Авторизация для API """
    user = await users_utils.get_user_by_email(form_data.username, db)

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email")

    if not users_utils.validate_password(
            password=form_data.password, hashed_password=user.password
    ):
        raise HTTPException(status_code=400, detail="Incorrect password")
    await users_utils.set_user_is_active(form_data.username, db)
    return await users_utils.create_user_token(user.id, db)


@router.post("/create-user/", response_model=users.UserCreate)
async def create_user(username: str = Form(), email: str = Form(), name: str = Form(), password: str = Form(),
                      db: Session = Depends(get_db)):
    """ Обработка создания пользователя для frontend """
    user = users.UserCreate(username=username, email=email, name=name, password=password)
    db_user = await users_utils.check_user_by_email(user.email, user.username, db)
    if db_user:
        raise HTTPException(status_code=400, detail="Email or username already registered")
    user_create = await users_utils.create_user(user, db)
    if user_create:
        return RedirectResponse("/create-user/", status_code=status.HTTP_302_FOUND)
    raise HTTPException(status_code=400, detail="User not created")


@router.post("/api/sign-up/", response_model=users.UserCreate)
async def create_user(user: users.UserCreate, db: Session = Depends(get_db)):
    db_user = await users_utils.check_user_by_email(user.email, user.username, db)
    if db_user:
        raise HTTPException(status_code=400, detail="Email or username already registered")
    return await users_utils.create_user(user, db)


@router.get("/api/users/me/", response_model=users.UserBase)
async def read_users_me(current_user: users.User = Depends(get_current_user_), db: Session = Depends(get_db)):
    """ API получения информации о пользователе по авторизованому токену """
    return current_user


@router.get("/api/users/all/", response_model=List[users.UserBase])
async def read_users_me(current_user: users.User = Depends(get_current_user_), db: Session = Depends(get_db)):
    """ API получения информации о всех пользователях по авторизованому токену """
    return await users_utils.get_users(db)


@router.get("/api/users/me/{token}", response_model=users.UserBase)
async def read_users_token(token: str, db: Session = Depends(get_db)):
    """ API получение информации о себе по токену в заголовке """
    return await get_current_user(token, db)


@router.get("/api/users/{token}", response_model=List[users.UserBase])
async def read_users_all_token(token: str, db: Session = Depends(get_db)):
    """ API получение информации по всем пользователям по токену в заголовке """
    return await get_users(token, db)
