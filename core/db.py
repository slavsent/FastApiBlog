from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from functools import lru_cache
from typing import Generator
from config import Settings
import os
import databases
from alembic import command
from alembic.config import Config
from sqlalchemy_utils import create_database, database_exists
from dotenv import load_dotenv

local = os.environ.get("LOCAL")
# testing = os.environ.get("TESTING")

dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.my-env')
#dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path)


database_host = os.environ.get("DB_HOST", "localhost")
database_pass = os.environ.get("DB_PASS")
database_type = os.environ.get('DB_TYPE')
database_user = os.environ.get('DB_USER')
database_name = os.environ.get('DB_NAME')
# database_test = os.environ.get('DB_TEST')

SQLALCHEMY_DATABASE_URL = f'{database_type}://{database_user}:{database_pass}@{database_host}/{database_name}'

# if testing:
#    SQLALCHEMY_DATABASE_URL = f'{database_type}://{database_user}:{database_pass}@{database_host}/{database_name}'
# else:
#    SQLALCHEMY_DATABASE_URL = f'{database_type}://{database_user}:{database_pass}@{database_host}/{database_test}'

if not database_exists(SQLALCHEMY_DATABASE_URL):
    create_database(SQLALCHEMY_DATABASE_URL)

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

Base = declarative_base()


@lru_cache
def create_session() -> scoped_session:
    session = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=engine),
    )
    return session


def get_db() -> Generator[scoped_session, None, None]:
    """
    Создание соединения с БД
    :return:
    """
    session = create_session()
    try:
        yield session
    finally:
        session.remove()
