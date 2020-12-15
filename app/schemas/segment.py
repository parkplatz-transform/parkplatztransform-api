from typing import Optional, List
import datetime

from pydantic import BaseModel
from geojson_pydantic.features import Feature
from geojson_pydantic.features import FeatureCollection
from geojson_pydantic.geometries import LineString as PydanticLineString

from ..models import Alignment, StreetLocation, UsageRestriction, NoParkingReason


class LineString(PydanticLineString):
    type: str = "LineString"


class SubsegmentBase(BaseModel):


    # parking_allowed = Column(Boolean, nullable=False)
    # order_number = Column(Integer, nullable=False)
    # length_in_meters = Column(Numeric(precision=2), default=0.00, nullable=False)
    # car_count = Column(Integer, default=0, nullable=False)
    # quality = Column(Integer, default=0, nullable=False)  # TODO: what actually is this?
    #
    # # Public parking allowed
    # fee = Column(Boolean, CheckConstraint("parking_allowed=TRUE"))
    # street_location = Column(Enum(StreetLocation), CheckConstraint("parking_allowed=TRUE"))
    # marked = Column(Boolean, CheckConstraint("parking_allowed=TRUE"))
    # alignment = Column(Enum(Alignment), CheckConstraint("parking_allowed=TRUE"))
    # duration_constraint = Column(Boolean, CheckConstraint("parking_allowed=TRUE"), default=False, nullable=False)
    # usage_restrictions = Column(Enum(UsageRestriction), CheckConstraint("parking_allowed=TRUE"))
    # time_constraint = Column(Boolean, CheckConstraint("parking_allowed=TRUE"), default=False, nullable=False)
    # time_constraint_reason = Column(Text, CheckConstraint("parking_allowed=TRUE"))
    #
    # # Public parking not allowed
    # no_parking_reason = Column(Enum(NoParkingReason), CheckConstraint("parking_allowed=FALSE"))

    parking_allowed: bool = True
    order_number: int = 0
    length_in_meters: float = 0
    car_count: int = 0
    quality: int = 1

    # Public parking allowed
    fee: bool = False
    street_location: StreetLocation = StreetLocation.street
    marked: bool = False
    alignment: Alignment = Alignment.parallel
    duration_constraint: bool = False
    usage_restrictions: Optional[UsageRestriction]
    time_constraint: bool = False
    time_constraint_reason: Optional[str]

    # Public parking not allowed
    no_parking_reason: Optional[NoParkingReason]


class Subsegment(SubsegmentBase):
    id: Optional[int]
    created_at: Optional[datetime.datetime]
    modified_at: Optional[datetime.datetime]


class SubsegmentsBase(BaseModel):
    subsegments: List[SubsegmentBase]


class Subsegments(BaseModel):
    subsegments: List[Subsegment]


class Segment(Feature):
    id: int
    properties: Subsegments
    geometry: LineString

    class Config:
        orm_mode = True


class SegmentCollection(FeatureCollection):
    features: List[Segment]


class SegmentBase(BaseModel):
    feature: Segment

    class Config:
        orm_mode = True


class SegmentCreate(BaseModel):
    type: str = "Feature"
    properties: SubsegmentsBase
    geometry: LineString


class SegmentUpdate(SegmentCreate):
    properties: Subsegments
