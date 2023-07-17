from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from core.db import engine, get_db
from modeling import models
from routers import users, blogs
from sqlalchemy.orm import Session
from modeling.models import Users
from utils import blogs as post_utils
from utils.dependencies import get_current_user_from_cookie
from utils import users as user_utils

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.absolute() / "static"),
    name="static",
)

templates = Jinja2Templates(directory="templates")

app.include_router(users.router, tags=['Users'])
app.include_router(blogs.router, tags=['Blogs'])


@app.get("/api/my_blog")
async def root():
    """ test страница """
    return {"message": "Welcome super blogs"}


@app.get("/", response_class=HTMLResponse)
async def login_read(request: Request):
    """
    Переход на станицу логина
    """
    return templates.TemplateResponse(
        "index.html", {"request": request}
    )


@app.get("/create-user/", response_class=HTMLResponse)
async def create_new_user(request: Request):
    """ Переход на страницу создания пользователя """
    return templates.TemplateResponse(
        "create_user.html", {"request": request}
    )


@app.get("/users/", response_class=HTMLResponse)
async def user_top_try(request: Request, db: Session = Depends(get_db)):
    """ Страница пользователя для просмотра блогов и работы со своими блогами """
    try:
        token = request.cookies.get("bearer")
    except Exception:
        token = None
    if token:
        user = await user_utils.get_user_by_token_(token, db)
        user_id = user.id
    else:
        user_id = None
    context = {
        "user_id": user_id,
        "request": request,
    }
    return templates.TemplateResponse("user_top.html", context)


@app.get("/user-info/", response_class=HTMLResponse)
async def user_info(request: Request, db: Session = Depends(get_db)):
    """ Страница просмотра информации о текущем пользователе """
    try:
        token = request.cookies.get("bearer")
    except Exception:
        token = None
    if token:
        user = await user_utils.get_user_by_token_(token, db)
        user_id = user.id
        db_user = db.query(Users).filter(Users.id == user_id).first()
    else:
        user_id = None
        db_user = None
    context = {
        "user_id": user_id,
        "request": request,
        "user": db_user,
    }
    return templates.TemplateResponse(
        "user_info.html", context
    )


@app.get("/users-info/", response_class=HTMLResponse)
async def user_info_all(request: Request, db: Session = Depends(get_db)):
    """ Страница просмотра информации о всех пользователях """
    try:
        token = request.cookies.get("bearer")
    except Exception:
        token = None
    if token:
        user = await user_utils.get_user_by_token_(token, db)
        user_id = user.id
        db_users = db.query(Users).all()
    else:
        user_id = None
        db_users = None
    context = {
        "user_id": user_id,
        "request": request,
        "users": db_users,
    }
    return templates.TemplateResponse(
        "users_info.html", context
    )


@app.get("/blogs/", response_class=HTMLResponse)
async def blog_info(request: Request, db: Session = Depends(get_db)):
    """ Страница просмотра всех блогов с возможностью поставить лайки """
    try:
        token = request.cookies.get("bearer")
    except Exception:
        token = None
    if token:
        user = await user_utils.get_user_by_token_(token, db)
        user_id = user.id
        total_count = await post_utils.get_posts_count(db)
        posts, likes = await post_utils.get_posts(db)
    else:
        user_id = None
        total_count = None
        posts = None
        likes = None

    context = {
        "user_id": user_id,
        "request": request,
        "total_count": total_count,
        "posts": posts,
        "likes_all": likes,
    }

    return templates.TemplateResponse(
        "blogs_info.html",
        context
    )


@app.get("/myblog/", response_class=HTMLResponse)
async def myblog_info(request: Request, db: Session = Depends(get_db)):
    """ Страница просмотра своих блогов и выбора редактирования или удаления """
    try:
        token = request.cookies.get("bearer")
    except Exception:
        token = None
    if token:
        user = await user_utils.get_user_by_token_(token, db)
        user_id = user.id
        total_count = await post_utils.get_posts_count_my(user_id, db)
        posts, likes = await post_utils.get_posts_my_front(user_id, db)
    else:
        user_id = None
        total_count = None
        posts = None
        likes = None
    context = {
        "user_id": user_id,
        "request": request,
        "total_count": total_count,
        "posts": posts,
        "likes_all": likes,
    }
    return templates.TemplateResponse(
        "my_blog_info.html",
        context
    )


@app.get("/myblog/new/", response_class=HTMLResponse)
async def create_blog(request: Request, db: Session = Depends(get_db)):
    """ Страница создания блога """
    try:
        token = request.cookies.get("bearer")
    except Exception:
        token = None
    if token:
        user = await user_utils.get_user_by_token_(token, db)
        user_id = user.id
        total_count = await post_utils.get_posts_count_my(user_id, db)
        posts, likes = await post_utils.get_posts_my_front(user_id, db)
    else:
        user_id = None
        total_count = None
        posts = None
        likes = None
    context = {
        "user_id": user_id,
        "request": request,
        "total_count": total_count,
        "posts": posts,
        "likes_all": likes,
    }
    return templates.TemplateResponse(
        "new_myblog.html",
        context
    )


@app.get("/myblog/edit/{post_id}/", response_class=HTMLResponse)
async def edit_blog(post_id: str, request: Request, db: Session = Depends(get_db)):
    """ Страница редактирования блога """
    try:
        token = request.cookies.get("bearer")
    except Exception:
        token = None
    if token:
        user = await user_utils.get_user_by_token_(token, db)
        user_id = user.id
        total_count = await post_utils.get_posts_count_my(user_id, db)
        posts, likes = await post_utils.get_posts_my(user_id, db)
        post_text = await post_utils.get_post(post_id, db)
        post_text = post_text.posts
    else:
        user_id = None
        total_count = None
        posts = None
        likes = None
        post_text = None
    context = {
        "user_id": user_id,
        "request": request,
        "total_count": total_count,
        "posts": posts,
        "likes_all": likes,
        "post_id": post_id,
        "post_text": post_text
    }
    return templates.TemplateResponse(
        "edit_myblog.html",
        context
    )
