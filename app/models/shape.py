from geoalchemy2.types import Geometry
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from .base_mixin import BaseMixin, Base


class Shape(BaseMixin, Base):
    __tablename__ = "shapes"

    area = Column(Geometry("POLYGON", 4326))
    line = Column(Geometry("LINESTRING", 4326))

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="shapes")

    recording_id = Column(Integer, ForeignKey("recordings.id"))
    recording = relationship("Recording", back_populates="shapes")
