from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from app.config import settings

DATABASE_URL = settings.database_url
if DATABASE_URL.startswith("postgres://"):
    # Hack - assumes the environment is heroku
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

engine = create_async_engine(DATABASE_URL, pool_size=20, max_overflow=0, future=True)

SessionLocal = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


# Dependency
async def get_db():
    async with SessionLocal() as db:
        yield db
