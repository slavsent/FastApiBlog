from Schemas.blogs import PostDetailsModel, PostModel, PostLike, PostDetailsModelLike
from Schemas.users import User
from utils import blogs as post_utils
from utils.dependencies import get_current_user, get_current_user_
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse, HTMLResponse
from core.db import get_db


router = APIRouter()


@router.get("/api/{user_id}/posts")
async def get_posts_users(user_id: str, db: Session = Depends(get_db)):
    """
    API получения информации о всех постах, при указади id пользователя
    :param user_id: id пользователя
    :param db: БД
    :return: информация о постах
    """
    total_count = await post_utils.get_posts_count(db)
    posts, likes = await post_utils.get_posts(db)
    return {"total_count": total_count, "results": posts, "likes_all": likes}


@router.get("/api/{user_id}/my_posts")
async def get_posts_user(user_id: str, db: Session = Depends(get_db)):
    """
    API получения информации о постах пользователя, при указади id пользователя
    :param user_id: id пользователя
    :param db: БД
    :return: информация о постах пользователя
    """
    total_count = await post_utils.get_posts_count_my(user_id, db)
    posts, likes = await post_utils.get_posts_my(user_id, db)
    return {"total_count": total_count, "results": posts, "likes_all": likes}


@router.get("/api/posts")
async def get_posts(db: Session = Depends(get_db)):
    """
    API получения информации о всех постах, ,без id пользователя и аторизации
    :param db: БД
    :return: информация о постах
    """
    total_count = await post_utils.get_posts_count(db)
    posts, likes = await post_utils.get_posts(db)
    return {"total_count": total_count, "results": posts, "likes_all": likes}


@router.get("/api/posts/post/{post_id}")
async def get_post(post_id: str, db: Session = Depends(get_db)):
    """
    Получения информации о конкретном посте по его id
    :param post_id: id поста
    :param db: БД
    :return: информация о посте
    """
    return await post_utils.get_post(post_id, db)


@router.get("/api/my_posts")
async def get_api_my_post(current_user: User = Depends(get_current_user_), db: Session = Depends(get_db)):
    """
    API получения информации о постах автаризованного пользователя
    :param current_user: пользователь
    :param db: БД
    :return: информация о постах
    """
    total_count = await post_utils.get_posts_count_my(current_user.id, db)
    posts, likes = await post_utils.get_posts_my(current_user.id, db)
    return {"total_count": total_count, "results": posts, "likes_all": likes}


@router.post("/api/posts/user/{user_id}", response_model=PostDetailsModel, status_code=201)
async def create_post_user(user_id: str, post: PostModel, db: Session = Depends(get_db)):
    """
    Создания поста по id пользователя
    :param user_id: id пользователя
    :param post: текст поста
    :param db: БД
    :return: информация о созданном посте
    """
    post_new = await post_utils.create_post_user(post, user_id, db)
    post_dict = {'id': post_new.id, 'dt_created': post_new.dt_created, 'posts': post_new.posts,
                 'user_id': post_new.user_id,
                 'dt_updated': post_new.dt_updated}
    return post_dict


@router.post("/api/posts", response_model=PostDetailsModel, status_code=201)
async def create_post(posts_text: PostModel, current_user: User = Depends(get_current_user_),
                      db: Session = Depends(get_db)):
    """
    API создание поста текущим авторизованным пользователем
    :param posts_text: текст поста
    :param current_user: авторизованный пользователь
    :param db: база данных
    :return: информация о созданном посте
    """
    post = await post_utils.create_post(posts_text, current_user.id, db)
    post_dict = {'id': post.id, 'dt_created': post.dt_created, 'posts': post.posts, 'user_id': post.user_id,
                 'dt_updated': post.dt_updated}
    return post_dict


@router.put("/api/edit-posts/{user_id}/{post_id}", response_model=PostDetailsModel)
async def update_post_user(posts_text: PostModel, user_id: str, post_id: str, db: Session = Depends(get_db)):
    """
    Редактирование поста по id пользователя и id поста
    :param user_id: id пользователя
    :param post_id: id поста
    :param posts_text: новый текст поста
    :param db: БД
    :return: информация о отредактированном посте
    """
    post_try = await post_utils.get_post_front(post_id, db)
    # проверка, что пост есть
    if not post_try:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This isn't post",
        )
    # проверка, что пользователь не редактировал чужие посты
    if str(post_try.user_id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to modify this post",
        )
    await post_utils.update_post_front(post_id, posts_text.posts_text, db)
    post = await post_utils.get_post(post_id, db)
    post_dict = {'id': post.id, 'dt_created': post.dt_created, 'posts': post.posts, 'user_id': post.user_id,
                 'dt_updated': post.dt_updated}
    return post_dict


@router.put("/api/edit-post/{post_id}", response_model=PostDetailsModel)
async def update_post_user_api(posts_text: PostModel, post_id: str, current_user: User = Depends(get_current_user_),
                               db: Session = Depends(get_db)):
    """
    Редактирование поста по автаризованным пользователем и id поста
    :param current_user: авторизованный пользователь
    :param post_id: id поста
    :param posts_text: новый текст поста
    :param db: БД
    :return: информация о отредактированном посте
    """
    post_try = await post_utils.get_post_front(post_id, db)
    # проверка, что пост есть
    if not post_try:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This isn't post",
        )
    # проверка, что пользователь не редактировал чужие посты
    if post_try.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to modify this post",
        )
    await post_utils.update_post_front(post_id, posts_text.posts_text, db)
    post = await post_utils.get_post(post_id, db)
    post_dict = {'id': post.id, 'dt_created': post.dt_created, 'posts': post.posts, 'user_id': post.user_id,
                 'dt_updated': post.dt_updated}
    return post_dict


@router.post("/myblog/edit/{user_id}/{post_id}/", response_model=PostDetailsModel)
async def update_post_user_front(user_id: str, post_id: str, post_text: str = Form(), db: Session = Depends(get_db)):
    """
    редактирование поста для frontend
    :param user_id: id пользователя
    :param post_id: id поста
    :param post_text: новый текст поста
    :param db: БД
    :return: информация о отредактированном посте
    """
    post_try = await post_utils.get_post_front(post_id, db)
    # проверка, что пост есть
    if not post_try:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This isn't post",
        )
    # проверка, что пользователь не редактировал чужие посты
    if str(post_try.user_id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to modify this post",
        )

    await post_utils.update_post_front(post_id, post_text, db)
    return RedirectResponse(f"/myblog/{user_id}", status_code=status.HTTP_302_FOUND)


@router.post('/api/like/{post_id}', status_code=201)
async def create_post_like(post_id: str, like: PostLike, current_user: User = Depends(get_current_user_),
                           db: Session = Depends(get_db)):
    """
    Простовление посту лайка авторизованым пользователем
    :param post_id: id поста
    :param like: лайк
    :param current_user: текущий авторизованный пользователь
    :param db: БД
    :return: информация о проставленом лайке
    """
    post_try = await post_utils.get_post_front(post_id, db)
    # проверка, что пост есть
    if not post_try:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This isn't post",
        )
    # проверка, что лайк ставится не своему посту
    if post_try.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't like self post",
        )
    like_on = await post_utils.get_like(post_id, current_user.id, db)
    # проверка на повторный лайк
    if like_on:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't like this post more one",
        )
    return await post_utils.create_post_like_api(post_id, current_user.id, bool(like.like), db)


@router.post("/api/like-create/{user_id}/{post_id}", status_code=201)
async def create_post_like_user(user_id: str, post_id: str, like: PostLike, db: Session = Depends(get_db)):
    """
    Простовление посту лайка по id пользователя
    :param post_id: id поста
    :param like: лайк
    :param user_id: id пользователя
    :param db: БД
    :return: информация о проставленом лайке
    """
    post_try = await post_utils.get_post_front(post_id, db)
    # проверка, что пост есть
    if not post_try:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This isn't post",
        )
    # проверка, что лайк ставится не своему посту
    if str(post_try.user_id) == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't like self post",
        )
    like_on = await post_utils.get_like(post_id, user_id, db)
    # проверка на повторный лайк
    if like_on:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't like this post more one",
        )
    return await post_utils.create_post_like(post_id, user_id, bool(like.like), db)


@router.get("/likes_true/{user_id}/{post_id}/")
async def create_post_likes_user_front_true(user_id: str, post_id: str, db: Session = Depends(get_db)):
    """
    Простовление посту лайка для frontend
    :param post_id: id поста
    :param user_id: id пользователя
    :param db: БД
    :return: информация о проставленом лайке
    """
    post = await post_utils.get_post_front(post_id, db)
    # проверка, что пост есть
    if not post:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This isn't post",
        )
    # проверка, что лайк ставится не своему посту
    if str(post.user_id) == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't like self post",
        )
    like_on = await post_utils.get_like(post_id, user_id, db)
    # проверка на повторный лайк
    if like_on:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't like this post more one",
        )
    like = True
    data = await post_utils.create_post_like_front(post_id, user_id, like, db)
    return RedirectResponse(f"/blogs/{user_id}", status_code=status.HTTP_302_FOUND)


@router.get("/likes_false/{user_id}/{post_id}/")
async def create_post_likes_user_front(user_id: str, post_id: str, db: Session = Depends(get_db)):
    """
    Простовление посту дислайка для frontend
    :param post_id: id поста
    :param user_id: id пользователя
    :param db: БД
    :return: информация о проставленом лайке
    """
    post = await post_utils.get_post_front(post_id, db)
    # проверка, что пост есть
    if not post:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This isn't post",
        )
    # проверка, что лайк ставится не своему посту
    if str(post.user_id) == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't like self post",
        )
    like_on = await post_utils.get_like(post_id, user_id, db)
    # проверка на повторный лайк
    if like_on:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't like this post more one",
        )
    like = False
    data = await post_utils.create_post_like_front(post_id, user_id, like, db)
    return RedirectResponse(f"/blogs/{user_id}", status_code=status.HTTP_302_FOUND)


@router.delete("/api/del-posts/{post_id}", status_code=status.HTTP_200_OK)
async def delete_post(
        post_id: str, current_user: User = Depends(get_current_user_), db: Session = Depends(get_db)
):
    """
    Удаление своего поста авторизованым пользователем
    :param post_id: id поста
    :param current_user: авторизованный пользователь
    :param db: БД
    :return: Удаление поста из БД
    """
    post = await post_utils.get_post(post_id, db)
    # проверка что такой пост есть
    if not post:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This isn't post",
        )
    # проверка что автор поста текущий пользователь
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't delete this post",
        )
    return await post_utils.delete_post(post_id, db)


@router.delete("/api/delete-posts/{user_id}/{post_id}", status_code=status.HTTP_200_OK)
async def delete_post_user(
        post_id: str, user_id: str, db: Session = Depends(get_db)
):
    """
    Удаление своего поста по id пользователя
    :param post_id: id поста
    :param user_id: id пользователя
    :param db: БД
    :return: Удаление поста из БД
    """
    post = await post_utils.get_post_front(post_id, db)
    # проверка что такой пост есть
    if not post:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This isn't post",
        )
    # проверка что автор поста текущий пользователь
    if str(post.user_id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't delete this post",
        )

    return await post_utils.delete_post(post_id, db)


@router.get("/myblog/delete/{user_id}/{post_id}", status_code=status.HTTP_200_OK)
async def delete_post_user_front(
        post_id: str, user_id: str, db: Session = Depends(get_db)
):
    """
    Удаление поста для frontend
    :param post_id: id поста
    :param user_id: id пользователя
    :param db: БД
    :return: удаление поста из БД
    """
    post = await post_utils.get_post_front(post_id, db)
    # проверка что такой пост есть
    if not post:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This isn't post",
        )
    # проверка что автор поста текущий пользователь
    if str(post.user_id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't delete this post",
        )
    data = await post_utils.delete_post(post_id, db)
    return RedirectResponse(f"/myblog/{user_id}", status_code=status.HTTP_302_FOUND)


@router.post("/myblog/new/{user_id}/")
async def create_post_user_front(user_id: str, post_text: str = Form(), db: Session = Depends(get_db)):
    """
    Создание нового поста для frontend
    :param user_id: id пользователя
    :param post_text: текст поста
    :param db: БД
    :return: Занесение в базу поста
    """
    post = await post_utils.create_post_front(post_text, user_id, db)
    return RedirectResponse(f"/myblog/{user_id}/", status_code=status.HTTP_302_FOUND)
