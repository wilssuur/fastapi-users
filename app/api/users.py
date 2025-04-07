from fastapi import Depends, HTTPException, APIRouter
from typing import Optional
import requests
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_session, SessionDep
from schemas import UserCreate, User, UserUpdate
from models import UserModel, EmailModel

router = APIRouter(prefix="/users", tags=["Пользователи"])


def get_age(name: str) -> Optional[int]:
    url = f"https://api.agify.io?name={name}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("age")
    except requests.ConnectionError:
        return None


def get_nationality(name: str) -> Optional[str]:
    url = f"https://api.nationalize.io/?name={name}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            nationality_data = response.json().get("country")
            if nationality_data:
                return nationality_data[0].get("country_id")
    except requests.ConnectionError:
        return None


def get_gender(name: str) -> Optional[str]:
    url = f"https://api.genderize.io?name={name}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("gender")

    except requests.ConnectionError:
        return None


@router.get(
    "/{last_name}",
    summary="Получить информацию о человеке по фамилии",
)
def get_user_by_last_name(last_name: str, session: SessionDep):
    users = (
        session.query(UserModel)
        .filter(UserModel.full_name.like(f"{last_name} %"))
        .all()
    )

    if not users:
        raise HTTPException(
            status_code=404, detail="Пользователь с такой фамилией не найден"
        )

    return [
        User(
            id=user.id,
            full_name=user.full_name,
            gender=user.gender,
            nationality=user.nationality,
            age=user.age,
            emails=[email.email for email in user.emails],
        )
        for user in users
    ]


@router.get("/", summary="Получить всех пользователей")
def get_users(session: SessionDep):
    query = select(UserModel)
    result = session.execute(query)
    users = result.scalars().all()
    if not users:
        return {"message": "Пользователей пока нет"}
    return [
        User(
            id=user.id,
            full_name=user.full_name,
            gender=user.gender,
            nationality=user.nationality,
            age=user.age,
            emails=[email.email for email in user.emails],
        )
        for user in users
    ]


@router.post("/", summary="Добавить нового пользователя")
def create_user(user_data: UserCreate, session: SessionDep):
    name_parts = user_data.full_name.split()
    if len(name_parts) < 2:
        raise HTTPException(
            status_code=400, detail="Необходимо ввести как минимум имя и фамилию"
        )

    existing_user = (
        session.query(UserModel)
        .filter(UserModel.full_name == user_data.full_name)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400, detail="Пользователь с таким ФИО уже существует"
        )

    first_name = name_parts[1]

    gender = get_gender(first_name)
    nationality = get_nationality(first_name)
    age = get_age(first_name)

    user = UserModel(
        full_name=user_data.full_name, gender=gender, nationality=nationality, age=age
    )

    session.add(user)
    session.commit()
    return {"ok": True, "message": "Новый пользователь добавлен"}


@router.put(
    "/{user_id}",
    summary="Обновить информацию о пользователе",
)
def update_user(
    user_id: int, user_data: UserUpdate, session: Session = Depends(get_session)
):
    user = session.query(UserModel).filter(UserModel.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user_data.full_name is not None:
        user.full_name = user_data.full_name

    if user_data.gender is not None:
        user.gender = user_data.gender

    if user_data.nationality is not None:
        user.nationality = user_data.nationality

    if user_data.age is not None:
        user.age = user_data.age

    if user_data.emails:
        for email in user.emails:
            session.delete(email)
        for email in user_data.emails:
            new_email = EmailModel(email=email, user_id=user.id)
            user.emails.append(new_email)

    session.commit()

    return {"ok": True, "message": "Информация о пользователе обновлена"}
