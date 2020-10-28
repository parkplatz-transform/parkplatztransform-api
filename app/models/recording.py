from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from .base_mixin import BaseMixin, Base


class Recording(BaseMixin, Base):
    __tablename__ = "recordings"

    quality = Column(Integer)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="recordings")

    segments = relationship("Segment", back_populates="recordings")
    shapes = relationship("Shape", back_populates="recordings")
