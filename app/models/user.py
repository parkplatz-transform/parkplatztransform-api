from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from .base_mixin import BaseMixin, Base

access_levels = {
    "guest": 0,
    "contributor": 1,
}


class User(BaseMixin, Base):
    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__()

    __tablename__ = "users"

    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    segments = relationship("Segment", back_populates="owner")
    sessions = relationship("UserSession", back_populates="owner")
    permission_level = Column(
        Integer, default=access_levels.get("guest"), nullable=False
    )


class UserSession(BaseMixin, Base):
    def __init__(self, user_id: str) -> None:
        self.owner_id = user_id
        super().__init__()

    __tablename__ = "sessions"
    owner_id = Column(
        "owner_id", UUID, ForeignKey("users.id"), nullable=False, index=True
    )
    owner = relationship("User", back_populates="sessions")
