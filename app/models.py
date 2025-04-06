from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str]
    gender: Mapped[str] = mapped_column(nullable=True)
    nationality: Mapped[str] = mapped_column(nullable=True)
    age: Mapped[int] = mapped_column(nullable=True)

    emails: Mapped[List["EmailModel"]] = relationship(
        "EmailModel", back_populates="user"
    )


class EmailModel(Base):
    __tablename__ = "emails"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped[UserModel] = relationship("UserModel", back_populates="emails")


class FriendshipModel(Base):
    __tablename__ = "friendship"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    friend_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
