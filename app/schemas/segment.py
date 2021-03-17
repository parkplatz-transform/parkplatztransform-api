from typing import Optional, List
import datetime

from pydantic import BaseModel, validator, root_validator
from geojson_pydantic.features import Feature
from geojson_pydantic.features import FeatureCollection
from geojson_pydantic.geometries import LineString as PydanticLineString

from ..models import (
    Alignment,
    StreetLocation,
    UserRestriction,
    NoParkingReason,
    AlternativeUsageReason,
)


class LineString(PydanticLineString):
    type: str = "LineString"


class SubsegmentBase(BaseModel):
    parking_allowed: bool
    order_number: int = 0
    length_in_meters: Optional[float]
    car_count: Optional[int]
    quality: int = 1

    # Public parking allowed
    fee: Optional[bool]
    street_location: Optional[StreetLocation]
    marked: Optional[bool]
    alignment: Optional[Alignment]
    duration_constraint: Optional[bool]
    user_restrictions: Optional[UserRestriction]
    alternative_usage_reason: Optional[AlternativeUsageReason]
    time_constraint: Optional[bool]
    time_constraint_reason: Optional[str]
    duration_constraint_reason: Optional[str]

    # Public parking not allowed
    no_parking_reasons: List[NoParkingReason] = []


class Subsegment(SubsegmentBase):
    id: Optional[str]
    created_at: Optional[datetime.datetime]
    modified_at: Optional[datetime.datetime]

    class Config:
        orm_mode = True


class SubsegmentsBase(BaseModel):
    subsegments: List[SubsegmentBase]


class Properties(BaseModel):
    subsegments: List[Subsegment]
    owner_id: Optional[str]


class Segment(Feature):
    id: str
    properties: Properties
    geometry: LineString

    class Config:
        orm_mode = True


class SegmentCollection(FeatureCollection):
    features: List[Segment]

    class Config:
        orm_mode = True


class SegmentBase(BaseModel):
    feature: Segment

    class Config:
        orm_mode = True


class SegmentCreate(BaseModel):
    type: str = "Feature"
    properties: SubsegmentsBase
    geometry: LineString


class SegmentUpdate(SegmentCreate):
    properties: Properties
