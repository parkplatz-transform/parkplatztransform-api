from sqlalchemy import (
    Column,
    ForeignKey,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry

from .base_mixin import BaseMixin, Base


class Segment(BaseMixin, Base):
    __tablename__ = "segments"

    owner_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="segments")

    further_comments = Column(Text)
    # data_source = Column(Enum())

    subsegments_non_parking = relationship(
        "SubsegmentNonParking", back_populates="segment", cascade="all, delete"
    )
    subsegments_parking = relationship(
        "SubsegmentParking", back_populates="segment", cascade="all, delete"
    )

    geometry = Column(Geometry(geometry_type="LINESTRING", srid=4326), nullable=False)
