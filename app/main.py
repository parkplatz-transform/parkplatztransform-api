import base64
from typing import List, Optional, Tuple

import time
from fastapi import Depends, FastAPI, HTTPException, BackgroundTasks, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.gzip import GZipMiddleware
from sqlalchemy.orm import Session

from .one_time_auth import OneTimeAuth, decode_jwt
from . import strings, schemas, controllers, email_service
from .database import SessionLocal
from .config import get_settings

app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=1000)

settings = get_settings()

one_time_auth = OneTimeAuth(
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


bearer_scheme = HTTPBearer()


async def verify_token(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    try:
        token_metadata = decode_jwt(token.credentials)
        assert token_metadata["exp"] > time.time()
    except Exception as e:
        raise HTTPException(401, strings.validation["unauthorized"])


@app.post("/users/", response_model=schemas.UserBase)
def send_magic_link(
    user: schemas.UserBase,
    background_tasks: BackgroundTasks,
):
    token = one_time_auth.generate_token(user.email)
    background_tasks.add_task(
        email_service.send_email_verification_link, user.email, token
    )
    return user


@app.get("/verify/", response_model=dict)
def verify_magic_link(code: str, email: str, db: Session = Depends(get_db)):
    if not one_time_auth.valid_token(code, email):
        raise HTTPException(401, strings.validation["unauthorized"])
    decoded = one_time_auth.get_decoded_token(code)
    if not controllers.get_user_by_email(db, email):
        controllers.create_user(db, schemas.UserBase(email=decoded["email"]))
    access_token = base64.b64decode(code).decode("utf8")
    return {"access_token": access_token, "token_type": "bearer"}


def parse_bounding_box(parameter: str) -> List[Tuple[str, str]]:
    spl = parameter.split(",")
    return list(zip(spl[0::2], spl[1::2]))


@app.get("/segments/", response_model=schemas.SegmentCollection)
async def read_segments(bbox: Optional[str] = None, db: Session = Depends(get_db)):
    if bbox:
        bbox = parse_bounding_box(bbox)
    db_recordings = controllers.get_segments(db, bbox=bbox)
    return db_recordings


@app.post(
    "/segments/", response_model=schemas.Segment, dependencies=[Depends(verify_token)]
)
def create_segment(
    segment: schemas.SegmentCreate,
    db: Session = Depends(get_db),
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    email = decode_jwt(token.credentials)["sub"]
    created_recording = controllers.create_segment(db=db, segment=segment, email=email)
    return created_recording
