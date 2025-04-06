from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from fastapi import Depends
from typing import Annotated
from sqlalchemy.orm import Session


DATABASE_URL = "sqlite:///users.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

new_session = sessionmaker(engine, expire_on_commit=False)


def get_session():
    with new_session() as session:
        yield session


class Base(DeclarativeBase):
    pass


SessionDep = Annotated[Session, Depends(get_session)]
