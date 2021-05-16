from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select

from .. import schemas

from ..models import User


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
