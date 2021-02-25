from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from .base_mixin import BaseMixin, Base

access = {
    'guest': 0,
    'contributor': 1,
    'developer': 2,
}


class User(BaseMixin, Base):
    __tablename__ = "users"

    email = Column(String, unique=True, index=True, nullable=False)
    segments = relationship("Segment", back_populates="owner")
    permission_level = Column(Integer, default=access.get('guest'), nullable=False)
