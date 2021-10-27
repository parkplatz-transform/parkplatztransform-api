from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

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
    permission_level = Column(
        Integer, default=access_levels.get("guest"), nullable=False
    )
