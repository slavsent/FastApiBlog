from datetime import datetime
from modeling.models import Users, Likes, UsersPosts
from Schemas import blogs as post_schema
from Schemas import users as users_schema
from sqlalchemy.orm import Session


async def create_post_user(post: post_schema.PostModel, user_id: str, db: Session):
    """
    Создание поста по user_id - str для api
    :param post:
    :param user_id:
    :param db:
    :return:
    """
    new_post = UsersPosts(user_id=user_id, posts=post.posts_text, dt_created=datetime.now(), dt_updated=datetime.now())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


async def create_post(post: post_schema.PostModel, user_id: users_schema.IdUser, db: Session):
    """
    создание поста для API для авторизованого пользователя
    :param post:
    :param user_id:
    :param db:
    :return:
    """
    new_post = UsersPosts(user_id=user_id, posts=post.posts_text, dt_created=datetime.now(), dt_updated=datetime.now())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    new_post = db.query(UsersPosts).filter(UsersPosts.posts == post.posts_text).first()
    return new_post


async def create_post_front(post: str, user_id: str, db: Session):
    """
    Создание поста по user_id - str для frontend тут пост уже str
    :param post:
    :param user_id:
    :param db:
    :return:
    """
    new_post = UsersPosts(user_id=user_id, posts=post, dt_created=datetime.now(), dt_updated=datetime.now())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


async def get_post(post_id: str, db: Session):
    """
    получение поста по id, с добавлением полей из таблицы Users
    :param post_id:
    :param db:
    :return:
    """
    posts = db.query(UsersPosts, Users).with_entities(UsersPosts.id, UsersPosts.user_id, Users.username,
                                                      UsersPosts.posts, UsersPosts.dt_created,
                                                      UsersPosts.dt_updated).filter(
        UsersPosts.user_id == Users.id, UsersPosts.id == post_id).first()
    return posts


async def get_post_front(post_id: str, db: Session):
    """
    получение поста по id
    :param post_id:
    :param db:
    :return:
    """
    posts = db.query(UsersPosts).filter(UsersPosts.id == post_id).first()
    return posts


async def get_posts(db: Session):
    """
    Получение всех постов и сколько есть лайков
    :param db:
    :return:
    """
    posts = db.query(UsersPosts, Users).with_entities(UsersPosts.id, Users.username, UsersPosts.posts,
                                                      UsersPosts.dt_created,
                                                      UsersPosts.dt_updated).filter(
        UsersPosts.user_id == Users.id).all()
    likes = db.query(UsersPosts, Likes).filter(UsersPosts.id == Likes.post_id, Likes.likes_on).count()
    return posts, likes


async def get_posts_count(db: Session):
    """
    получения количества постов
    :param db:
    :return:
    """
    posts_count = db.query(UsersPosts).count()
    return posts_count


async def get_posts_my(user_id: str, db: Session):
    """
    получения постов определенного пользователя и лайков по его постам
    :param user_id:
    :param db:
    :return:
    """
    posts = db.query(UsersPosts, Users).with_entities(Users.username, UsersPosts.posts, UsersPosts.dt_created,
                                                      UsersPosts.dt_updated).filter(UsersPosts.user_id == Users.id,
                                                                                    UsersPosts.user_id == user_id).all()
    likes = db.query(UsersPosts, Likes).filter(UsersPosts.id == Likes.post_id, Likes.likes_on,
                                               UsersPosts.user_id == user_id).count()
    return posts, likes


async def get_posts_my_front(user_id: str, db: Session):
    """
    получения постов определенного пользователя и лайков по его постам для frontend другой набор полей
    :param user_id:
    :param db:
    :return:
    """
    posts = db.query(UsersPosts).filter(UsersPosts.user_id == user_id).all()
    likes = db.query(UsersPosts, Likes).filter(UsersPosts.id == Likes.post_id, Likes.likes_on,
                                               UsersPosts.user_id == user_id).count()
    return posts, likes


async def get_posts_count_my(user_id: str, db: Session):
    """
    получение количества постов определенного пользователя
    :param user_id:
    :param db:
    :return:
    """
    posts_count = db.query(UsersPosts).filter(UsersPosts.user_id == user_id).count()
    return posts_count


async def update_post_front(post_id: str, post: str, db: Session):
    """
    изменения поста для frontend и одного из api
    :param post_id:
    :param post:
    :param db:
    :return:
    """
    posts = db.query(UsersPosts).filter(UsersPosts.id == post_id).first()
    posts.posts = post
    posts.dt_updated = datetime.now()
    db.commit()
    db.refresh(posts)
    return posts


async def update_post(post_id: str, post: post_schema.PostModel, db: Session):
    """
    изменение поста для одного из api
    :param post_id:
    :param post:
    :param db:
    :return:
    """
    posts = db.query(UsersPosts).filter(UsersPosts.id == post_id).first()
    posts.posts = post.posts_text
    posts.dt_updated = datetime.now()
    db.commit()
    db.refresh(posts)
    return posts


async def create_post_like(post_id: str, user_id: str, like: post_schema.PostLike, db: Session):
    """
    создание лайка для поста
    :param post_id:
    :param user_id:
    :param like:
    :param db:
    :return:
    """
    new_like = Likes(user_id=user_id, post_id=post_id, likes_on=like)
    db.add(new_like)
    db.commit()
    db.refresh(new_like)
    post_like = db.query(UsersPosts, Likes).with_entities(UsersPosts.user_id, UsersPosts.posts, UsersPosts.dt_created,
                                                          UsersPosts.dt_updated, Likes.likes_on).filter(
        UsersPosts.id == Likes.post_id, UsersPosts.id == post_id).first()
    return post_like


async def create_post_like_api(post_id: str, user_id: users_schema.IdUser, like: post_schema.PostLike, db: Session):
    """
    создание лайка для поста для API
    :param post_id:
    :param user_id:
    :param like:
    :param db:
    :return:
    """
    new_like = Likes(user_id=user_id, post_id=post_id, likes_on=like)
    db.add(new_like)
    db.commit()
    db.refresh(new_like)
    post_like = db.query(UsersPosts, Likes).with_entities(UsersPosts.user_id, UsersPosts.posts, UsersPosts.dt_created,
                                                          UsersPosts.dt_updated, Likes.likes_on).filter(
        UsersPosts.id == Likes.post_id, UsersPosts.id == post_id).first()
    return post_like


async def create_post_like_front(post_id: str, user_id: str, like: bool, db: Session):
    """
    создание лайка для поста для frontend
    :param post_id:
    :param user_id:
    :param like:
    :param db:
    :return:
    """
    new_like = Likes(user_id=user_id, post_id=post_id, likes_on=like)
    db.add(new_like)
    db.commit()
    db.refresh(new_like)
    post_like = db.query(UsersPosts, Likes).with_entities(UsersPosts.user_id, UsersPosts.posts, UsersPosts.dt_created,
                                                          UsersPosts.dt_updated, Likes.likes_on).filter(
        UsersPosts.id == Likes.post_id, UsersPosts.id == post_id).first()
    return post_like


async def get_user_id(username: str, db: Session):
    """
    получение id пользователя по username
    :param username:
    :param db:
    :return:
    """
    user = db.query(Users).filter(UsersPosts.username == username).first()
    return user.id


async def get_like(post_id: str, user_id: str, db: Session):
    """
    для проверки на повторный лайк пользователем
    :param post_id:
    :param user_id:
    :param db:
    :return:
    """
    like_try = db.query(Likes).filter(Likes.user_id == user_id, Likes.post_id == post_id).first()
    if not like_try:
        like_try = False
    return like_try


async def delete_post(post_id: str, db: Session):
    """
    удаление поста
    :param post_id:
    :param db:
    :return:
    """
    likes = db.query(Likes).filter(Likes.post_id == post_id)
    likes.delete(synchronize_session=False)
    posts = db.query(UsersPosts).filter(UsersPosts.id == post_id)
    posts.delete(synchronize_session=False)
    db.commit()
    return {"status_code": True, "message": "The post has been deleted"}
