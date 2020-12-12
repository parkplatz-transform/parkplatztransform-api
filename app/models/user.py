from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from .base_mixin import BaseMixin, Base


class User(BaseMixin, Base):
    __tablename__ = "users"

    email = Column(String, unique=True, index=True, nullable=False)
    segments = relationship("Segment", back_populates="owner")
