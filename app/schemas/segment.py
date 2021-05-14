from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel
from geojson_pydantic.features import Feature
from geojson_pydantic.features import FeatureCollection
from geojson_pydantic.geometries import Geometry

from ..models import (
    Alignment,
    StreetLocation,
    UserRestriction,
    NoParkingReason,
    AlternativeUsageReason,
)


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
    user_restriction: Optional[bool]
    user_restriction_reason: Optional[UserRestriction]
    alternative_usage_reason: Optional[AlternativeUsageReason]
    time_constraint: Optional[bool]
    time_constraint_reason: Optional[str]
    duration_constraint_reason: Optional[str]

    # Public parking not allowed
    no_parking_reasons: List[NoParkingReason] = []


class Subsegment(SubsegmentBase):
    class Config:
        orm_mode = True


class SubsegmentsBase(BaseModel):
    subsegments: List[SubsegmentBase]


class Properties(BaseModel):
    subsegments: List[Subsegment]
    has_subsegments: bool
    owner_id: Optional[str]
    data_source: Optional[str]
    further_comments: Optional[str]
    modified_at: Optional[str]
    created_at: Optional[str]


class Segment(Feature):
    id: str
    properties: Properties
    geometry: Geometry

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
    properties: Properties
    geometry: Geometry


class SegmentUpdate(SegmentCreate):
    properties: Properties


class SegmentQuery(BaseModel):
    bbox: str
    details: bool
    exclude_ids: List[str]
    include_if_modified_after: Optional[datetime]
