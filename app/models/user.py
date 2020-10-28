from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from ..database import Base
from .base_mixin import BaseMixin


class User(BaseMixin, Base):
    __tablename__ = "users"

    email = Column(String, unique=True, index=True)
    name = Column(String)

    recordings = relationship("Recording", back_populates="user")
