from fastapi import FastAPI
import uvicorn

from database import engine, Base
from api import users, emails, friends

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(users.router)
app.include_router(emails.router)
app.include_router(friends.router)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
