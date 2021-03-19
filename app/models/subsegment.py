import enum

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    Enum,
    Numeric,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import relationship

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


class UserRestriction(str, enum.Enum):
    all_users = "all_users"
    handicap = "handicap"
    residents = "residents"
    car_sharing = "car_sharing"
    gender = "gender"
    electric_cars = "electric_cars"
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


class SubsegmentNonParking(BaseMixin, Base):
    def __init__(self, subsegment, segment_id: str, order_number: int) -> None:
        self.order_number = order_number
        self.length_in_meters = subsegment.length_in_meters
        self.quality = subsegment.quality
        self.no_parking_reasons = subsegment.no_parking_reasons
        self.segment_id = segment_id
        super().__init__()

    __tablename__ = "subsegments_non_parking"

    parking_allowed = False
    order_number = Column(Integer, nullable=False)

    length_in_meters = Column(Numeric(scale=6, precision=2))

    quality = Column(Integer, default=0, nullable=False)

    no_parking_reasons = Column(ARRAY(Enum(NoParkingReason)))

    segment_id = Column(
        UUID, ForeignKey("segments.id", ondelete="CASCADE"), nullable=False
    )
    segment = relationship("Segment", back_populates="subsegments_non_parking")


class SubsegmentParking(BaseMixin, Base):
    def __init__(self, subsegment, segment_id: str, order_number: int) -> None:
        self.order_number = order_number
        self.length_in_meters = subsegment.length_in_meters
        self.car_count = subsegment.car_count
        self.quality = subsegment.quality
        self.fee = subsegment.fee
        self.street_location = subsegment.street_location
        self.marked = subsegment.marked
        self.alignment = subsegment.alignment
        self.user_restriction = subsegment.user_restriction
        self.user_restriction_reason = subsegment.user_restriction_reason
        self.alternative_usage_reason = subsegment.alternative_usage_reason
        self.time_constraint = subsegment.time_constraint
        self.time_constraint_reason = subsegment.time_constraint_reason

        self.duration_constraint = subsegment.duration_constraint
        self.duration_constraint_reason = subsegment.duration_constraint_reason

        self.segment_id = segment_id
        super().__init__()

    __tablename__ = "subsegments_parking"

    parking_allowed = True
    order_number = Column(Integer, nullable=False)

    length_in_meters = Column(Numeric(scale=6, precision=2))
    car_count = Column(Integer)

    quality = Column(Integer, default=0, nullable=False)

    fee = Column(Boolean)
    street_location = Column(Enum(StreetLocation))
    marked = Column(Boolean)
    alignment = Column(Enum(Alignment))
    alternative_usage_reason = Column(Enum(AlternativeUsageReason))
    
    user_restriction = Column(Boolean)
    user_restriction_reason = Column(Enum(UserRestriction))

    time_constraint = Column(Boolean)
    time_constraint_reason = Column(Text)

    duration_constraint = Column(Boolean)
    duration_constraint_reason = Column(Text)

    segment_id = Column(
        UUID, ForeignKey("segments.id", ondelete="CASCADE"), nullable=False
    )
    segment = relationship("Segment", back_populates="subsegments_parking")
