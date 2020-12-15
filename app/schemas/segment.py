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
