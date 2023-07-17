from datetime import datetime

from pydantic import BaseModel, UUID4


class PostModel(BaseModel):
    """ Validate request data """
    posts_text: str


class PostDetailsModel(BaseModel):
    """ Return response data """
    dt_created: datetime
    posts: str
    user_id: UUID4
    dt_updated: datetime


class PostLike(BaseModel):
    """ Validate request data """
    like: bool


class PostDetailsModelLike(PostDetailsModel):
    """ Return response data """
    like: bool

