import enum

from sqlalchemy import Boolean, Column, ForeignKey, Integer, Enum
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry

from .base_mixin import BaseMixin, Base


class Alignment(str, enum.Enum):
    parallel = "parallel"
    perpendicular = "perpendicular"
    diagonal = "diagonal"


class StreetLocation(str, enum.Enum):
    street = "street"
    curb = "curb"
    sidewalk = "sidewalk"
    parking_bay = "parking_bay"
    middle = "middle"
    car_park = "car_park"


class Subsegment(BaseMixin, Base):
    __tablename__ = "subsegments"

    order_number = Column(Integer)
    parking_allowed = Column(Boolean)
    marked = Column(Boolean)
    alignment = Column(Enum(Alignment))
    street_location = Column(Enum(StreetLocation))
    length_in_meters = Column(Integer)
    car_count = Column(Integer)
    count = Column(Integer)
    quality = Column(Integer)

    segment_id = Column(Integer, ForeignKey("segments.id", ondelete="CASCADE"))
    segment = relationship("Segment", back_populates="subsegments")


class Segment(BaseMixin, Base):
    __tablename__ = "segments"

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="segments")

    subsegments = relationship(
        "Subsegment", back_populates="segment", cascade="all, delete"
    )
    geometry = Column(Geometry(geometry_type="LINESTRING", srid=4326))
