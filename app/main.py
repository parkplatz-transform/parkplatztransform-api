from typing import List

import graphene
from starlette.graphql import GraphQLApp
from pypale import Pypale
from fastapi import Depends, FastAPI, HTTPException, Header
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine
from config import get_settings

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

token_ttl_minutes = 14 * 24 * 60        # 2 weeks
token_issue_ttl_seconds = 2 * 60 * 60   # 2 hours


pypale = Pypale(
    base_url="localhost:8023",
    secret_key=get_settings().secret_key,
    token_ttl_minutes=token_ttl_minutes,
    token_issue_ttl_seconds=token_issue_ttl_seconds
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def authenticate(token: str):
    valid = pypale.valid_token(token)
    print(valid)
    if not valid:
        raise HTTPException(status_code=401, detail="Forbidden")


@app.post("/users/", response_model=schemas.UserCreate)
def create_user(user: schemas.UserBase, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    token = pypale.generate_token(user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud.create_user(db=db, user=user)
    user.token = token
    return user


@app.get("/users/{user_id}", response_model=schemas.User)
async def read_user(user_id: int, db: Session = Depends(get_db), token = Header(None)):
    db_user = crud.get_user(db, user_id=user_id)
    valid = await authenticate(token)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


class Query(graphene.ObjectType):
    hello = graphene.String(name=graphene.String(default_value="stranger"))

    def resolve_hello(self, info, name):
        return "Hello " + name

app.add_route("/graphql", GraphQLApp(schema=graphene.Schema(query=Query)))
