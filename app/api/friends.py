from fastapi import APIRouter, HTTPException

from models import FriendshipModel, UserModel
from database import SessionDep

router = APIRouter(prefix="/users/{user_id}/friends", tags=["Друзья"])


@router.post(
    "/{friend_id}",
    summary="Создать дружеские отношения",
)
def add_friend(user_id: int, friend_id: int, session: SessionDep):
    user = session.get(UserModel, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    friend = session.get(UserModel, friend_id)
    if not friend:
        raise HTTPException(
            status_code=404, detail="Пользователь для дружеских отношений не найден"
        )

    if user_id == friend_id:
        raise HTTPException(status_code=400, detail="Нельзя добавить себя в друзья")

    existing_friendship = (
        session.query(FriendshipModel)
        .filter(
            (FriendshipModel.user_id == user_id)
            & (FriendshipModel.friend_id == friend_id)
        )
        .first()
    )

    if existing_friendship:
        raise HTTPException(status_code=400, detail="Эти пользователи уже друзья")

    friendship = FriendshipModel(user_id=user_id, friend_id=friend_id)
    reverse_friendship = FriendshipModel(user_id=friend_id, friend_id=user_id)

    session.add(friendship)
    session.add(reverse_friendship)
    session.commit()

    return {"ok": True, "message": "Дружеские отношения успешно созданы"}


@router.get("/", summary="Получить друзей пользователя")
def get_friend(user_id: int, session: SessionDep):
    user = session.get(UserModel, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    friends = (
        session.query(UserModel)
        .join(FriendshipModel, UserModel.id == FriendshipModel.friend_id)
        .filter(FriendshipModel.user_id == user_id)
        .all()
    )

    if not friends:
        return {"message": "У пользователя пока нет друзей"}

    return [
        {
            "id": friend.id,
            "full_name": friend.full_name,
            "age": friend.age,
            "gender": friend.gender,
            "emails": [email.email for email in friend.emails],
        }
        for friend in friends
    ]
