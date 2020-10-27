from typing import List

import graphene
from starlette.graphql import GraphQLApp, GraphQLError
from fastapi import Depends, FastAPI, HTTPException, Header
from sqlalchemy.orm import Session
from email_validator import validate_email, EmailNotValidError

from .pypale import Pypale
from . import crud, models, schemas, strings
from .email_service import send_verification
from .database import SessionLocal, engine
from config import get_settings

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

settings = get_settings()

pypale = Pypale(
    base_url=settings.base_url,
    secret_key=settings.secret_key,
    token_ttl_minutes=int(settings.token_ttl_minutes),
    token_issue_ttl_seconds=int(settings.token_issue_ttl_seconds),
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
    if not valid:
        raise GraphQLError(strings.validation.forbidden)


class CreateUser(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)

    ok = graphene.Boolean()
    """
    Token should eventually be delivered via email
    """
    # token = graphene.String()

    @staticmethod
    def mutate(root, info, email):
        try:
            valid = validate_email(email)
            email = valid.email
        except EmailNotValidError as e:
            raise GraphQLError(str(e))
        db = SessionLocal()
        db_user = crud.get_user_by_email(db, email=email)
        if db_user:
            raise GraphQLError(strings.validation["email_in_use"])
        token = pypale.generate_token(email)

        # user = crud.create_user(db=db, user=schemas.UserBase(email=email))
        send_verification(email, token)
        return CreateUser(ok=True)


class Query(graphene.ObjectType):
    get_lines = graphene.String(name=graphene.String(default_value="noop"))

    def resolve_hello(self, info):
        return "Noop"


class Mutations(graphene.ObjectType):
    create_user = CreateUser.Field()


graphql_app = GraphQLApp(schema=graphene.Schema(query=Query, mutation=Mutations))
app.add_route("/", graphql_app)
