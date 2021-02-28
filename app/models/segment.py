import enum

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    Enum,
    Numeric,
    Text,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry

from .base_mixin import BaseMixin, Base


class Alignment(str, enum.Enum):
    parallel = "parallel"
    perpendicular = "perpendicular"
    diagonal = "diagonal"
    unknown = "unknown"


class StreetLocation(str, enum.Enum):
    street = "street"
    curb = "curb"
    sidewalk = "sidewalk"
    parking_bay = "parking_bay"
    middle = "middle"
    car_park = "car_park"
    unknown = "unknown"


class UserRestriction(str, enum.Enum):
    all_users = "all_users"
    handicap = "handicap"
    residents = "residents"
    car_sharing = "car_sharing"
    gender = "gender"
    electric_cars = "electric_cars"
    unknown = "unknown"
    other = "other"


class NoParkingReason(str, enum.Enum):
    private_parking = "private_parking"
    bus_stop = "bus_stop"
    bus_lane = "bus_lane"
    taxi = "taxi"
    tree = "tree"
    bike_racks = "bike_racks"
    pedestrian_crossing = "pedestrian_crossing"
    pedestrian_zone = "pedestrian_zone"
    driveway = "driveway"
    loading_zone = "loading_zone"
    standing_zone = "standing_zone"
    emergency_exit = "emergency_exit"
    lowered_curb_side = "lowered_curb_side"
    no_stopping = "no_stopping"
    lane = "lane"


class AlternativeUsageReason(str, enum.Enum):
    bus_stop = "bus_stop"
    bus_lane = "bus_lane"
    market = "market"
    lane = "lane"
    taxi = "taxi"
    loading = "loading"
    other = "other"


class Subsegment(BaseMixin, Base):
    __tablename__ = "subsegments"

    parking_allowed = Column(Boolean, nullable=True)
    order_number = Column(Integer, nullable=False)
    length_in_meters = Column(Numeric(precision=2))
    car_count = Column(Integer)
    quality = Column(Integer, default=0, nullable=False)  # TODO: what actually is this?

    # Public parking allowed
    fee = Column(Boolean, CheckConstraint("parking_allowed=TRUE"))
    street_location = Column(
        Enum(StreetLocation), CheckConstraint("parking_allowed=TRUE")
    )
    marked = Column(Boolean, CheckConstraint("parking_allowed=TRUE"), nullable=True)
    alignment = Column(Enum(Alignment), CheckConstraint("parking_allowed=TRUE"))
    duration_constraint = Column(
        Boolean, CheckConstraint("parking_allowed=TRUE"), nullable=True, default=None
    )
    user_restrictions = Column(
        Enum(UserRestriction), CheckConstraint("parking_allowed=TRUE")
    )
    alternative_usage_reason = Column(
        Enum(AlternativeUsageReason), CheckConstraint("parking_allowed=TRUE")
    )

    time_constraint = Column(
        Boolean, CheckConstraint("parking_allowed=TRUE"), nullable=True
    )
    time_constraint_reason = Column(Text, CheckConstraint("parking_allowed=TRUE"))

    duration_constraint_details = Column(Text)

    # Public parking not allowed
    no_parking_reasons = Column(
        ARRAY(Enum(NoParkingReason)), CheckConstraint("parking_allowed=FALSE")
    )

    segment_id = Column(
        Integer, ForeignKey("segments.id", ondelete="CASCADE"), nullable=False
    )
    segment = relationship("Segment", back_populates="subsegments")


class Segment(BaseMixin, Base):
    __tablename__ = "segments"

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="segments")

    subsegments = relationship(
        "Subsegment", back_populates="segment", cascade="all, delete"
    )
    geometry = Column(Geometry(geometry_type="LINESTRING", srid=4326), nullable=False)
