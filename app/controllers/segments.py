import uuid
from typing import List, Tuple

from sqlalchemy.orm import Session, noload, joinedload
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import LineString, Polygon

from .. import schemas
from ..models import Segment, SubsegmentNonParking, SubsegmentParking


def serialize_segment(segment: Segment) -> schemas.Segment:
    shape = to_shape(segment.geometry)
    return schemas.Segment(
        id=segment.id,
        properties={
            "subsegments": segment.subsegments_parking + segment.subsegments_non_parking,
            "owner_id": segment.owner_id,
        },
        geometry={"coordinates": shape.coords[:]},
        bbox=shape.bounds,
    )


def get_segments(
    db: Session,
    bbox: List[Tuple[float, float]] = None,
    exclude: List[int] = None,
    details: bool = True,
) -> schemas.SegmentCollection:
    segments = db.query(Segment).options(
        joinedload(Segment.subsegments_parking),
        joinedload(Segment.subsegments_non_parking),
        noload(Segment.subsegments_parking if not details else None),
        noload(Segment.subsegments_non_parking if not details else None),
    )
    if exclude:
        segments = segments.filter(Segment.id.notin_(exclude))
    if bbox:
        polygon = from_shape(Polygon(bbox), srid=4326)
        segments = segments.filter(polygon.ST_Intersects(Segment.geometry))
    collection = list(map(lambda feat: serialize_segment(feat), segments))
    return schemas.SegmentCollection(features=collection)


def create_subsegments(db: Session, subsegments, segment_id: str):
    for idx, subsegment in enumerate(subsegments):
        if subsegment.parking_allowed:
            db_prop = SubsegmentParking(
                segment_id=segment_id, 
                subsegment=subsegment,
                order_number=idx,
            )
            db.add(db_prop)
        else:
            db_prop = SubsegmentNonParking(
                segment_id=segment_id, 
                subsegment=subsegment,
                order_number=idx,
            )
            db.add(db_prop)


def create_segment(
    db: Session, segment: schemas.SegmentCreate, user_id: str
) -> schemas.Segment:
    geometry = from_shape(
        LineString(coordinates=segment.geometry.coordinates), srid=4326
    )

    db_segment = Segment()
    db_segment.geometry = geometry
    db_segment.owner_id = user_id

    db.add(db_segment)
    db.commit()
    db.refresh(db_segment)

    create_subsegments(db, segment.properties.subsegments, db_segment.id)
    
    db.commit()
    return serialize_segment(db_segment)


def update_segment(
    db: Session, segment_id: str, segment: schemas.SegmentCreate, user_id: str
) -> schemas.Segment:
    geometry = from_shape(
        LineString(coordinates=segment.geometry.coordinates), srid=4326
    )

    db_segment = db.query(Segment).get(segment_id)

    db.query(SubsegmentNonParking).filter(SubsegmentNonParking.segment_id == segment_id).delete()
    db.query(SubsegmentParking).filter(SubsegmentParking.segment_id == segment_id).delete()

    create_subsegments(db, segment.properties.subsegments, db_segment.id)

    db_segment.geometry = geometry
    db_segment.owner_id = user_id

    db.commit()
    db.refresh(db_segment)
    return serialize_segment(db_segment)


def delete_segment(db: Session, segment_id: str):
    segment = db.query(Segment).filter(Segment.id == segment_id).first()
    db.delete(segment)
    db.commit()
    return segment


def get_segment(db: Session, segment_id: str):
    segment = db.query(Segment).get(segment_id)
    return serialize_segment(segment)
