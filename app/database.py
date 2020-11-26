from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import get_settings

DATABASE_URL = (
    get_settings().database_url
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
