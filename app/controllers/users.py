from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import delete, select

from .. import schemas

from ..models import User, UserSession


def get_user(db: Session, user_id: str) -> User:
    return db.query(User).filter(User.id == user_id).first()


async def get_user_by_email(db: Session, email: str) -> User:
    query = await db.execute((
        select(User)
        .where(User.email == email)
    ))
    return query.scalars().first()


async def create_user(db: Session, user: schemas.UserBase) -> User:
    db_user = User(email=user.email)
    db.add(db_user)
    await db.commit()
    await db.flush()
    await db.refresh(db_user)
    return db_user


async def create_session(db: Session, user_id: str) -> str:
    db_session = UserSession(user_id=user_id)
    db.add(db_session)
    await db.commit()
    return db_session.id


async def get_logged_in_user(db: Session, session_id: str) -> schemas.User:
    query = await db.execute(
        select(User)
        .join(User.sessions)
        .where(UserSession.id == session_id)
    )
    return query.scalars().first()


async def clear_session(db: Session, session_id: str):
    await db.execute(
        delete(UserSession)
        .where(UserSession.id == session_id)
    )
    return session_id
