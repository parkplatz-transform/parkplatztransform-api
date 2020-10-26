from typing import List

import graphene
from starlette.graphql import GraphQLApp, GraphQLError
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


class CreateUser(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)

    ok = graphene.Boolean()
    token = graphene.String()

    @staticmethod
    def mutate(root, info, email):
        db = SessionLocal()
        db_user = crud.get_user_by_email(db, email=email)
        token = pypale.generate_token(email)
        if db_user:
            return GraphQLError("Email already registered")
        user = crud.create_user(db=db, user=schemas.UserBase(email=email))
        user.token = token
        return CreateUser(token=token, ok=True)


class Query(graphene.ObjectType):
    get_lines = graphene.String(name=graphene.String(default_value="noop"))

    def resolve_hello(self, info):
        return "Noop"

class Mutations(graphene.ObjectType):
    create_user = CreateUser.Field()

app.add_route("/graphql", GraphQLApp(schema=graphene.Schema(query=Query, mutation=Mutations)))
