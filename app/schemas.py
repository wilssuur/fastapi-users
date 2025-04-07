from typing import List, Optional
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    full_name: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    gender: Optional[str] = None
    nationality: Optional[str] = None
    age: Optional[int] = None
    emails: List[EmailStr]

    class Config:
        orm_mode = True


class UserUpdate(UserBase):
    full_name: Optional[str] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    age: Optional[int] = None
    emails: Optional[List[EmailStr]] = None

    class Config:
        orm_mode = True


class EmailCreate(BaseModel):
    email: EmailStr
