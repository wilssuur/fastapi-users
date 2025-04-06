from fastapi import APIRouter, HTTPException

from models import EmailModel, UserModel
from schemas import EmailCreate
from database import SessionDep

router = APIRouter(prefix="/users/{user_id}/emails", tags=["Почтовые ящики"])


@router.post("/", summary="Добавить почтовый ящик пользователю")
def add_email(user_id: int, email: EmailCreate, session: SessionDep):
    user = session.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    existing_email = (
        session.query(EmailModel)
        .filter(EmailModel.email == email.email, EmailModel.user_id == user_id)
        .first()
    )
    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Этот почтовый ящик уже добавлен для данного пользователя",
        )

    email = EmailModel(email=email.email, user_id=user_id)
    session.add(email)
    session.commit()

    return {"ok": True, "message": "Почтовый ящик добавлен"}
