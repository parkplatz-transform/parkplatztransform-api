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
    parking_allowed: bool = True
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
    duration_constraint_details: Optional[str]

    # Public parking not allowed
    no_parking_reasons: List[NoParkingReason] = []

    @validator("no_parking_reasons", pre=True)
    def replace_none_with_empty_list(cls, value):
        return [] if value is None else value

    @validator("street_location", "alignment", "alternative_usage_reason", pre=True)
    def replace_unknown_with_null(cls, value):
        return None if value == "unknown" else value

    @root_validator(pre=True)
    def enforce_parking_not_allowed(cls, values):
        if values["parking_allowed"]:
            assert (
                values.get("no_parking_reasons") is None
                or len(values["no_parking_reasons"]) == 0
            ), "no_parking_reasons incompatible with parking_allowed=true"
        else:
            assert (
                values.get("alternative_usage_reason") is None
            ), "alternative_usage_reason incompatible with parking_allowed=false"
        return values


class Subsegment(SubsegmentBase):
    id: Optional[int]
    created_at: Optional[datetime.datetime]
    modified_at: Optional[datetime.datetime]

    class Config:
        orm_mode = True


class SubsegmentsBase(BaseModel):
    subsegments: List[SubsegmentBase]


class Properties(BaseModel):
    subsegments: List[Subsegment]
    owner_id: int


class Segment(Feature):
    id: int
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
