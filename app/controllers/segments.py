from typing import List, Tuple

from sqlalchemy.orm import Session, noload, joinedload
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import LineString, Polygon

from .. import schemas
from ..models import Segment, Subsegment


def serialize_segment(segment: Segment) -> schemas.Segment:
    shape = to_shape(segment.geometry)
    return schemas.Segment(
        id=segment.id,
        properties={
            "subsegments": segment.subsegments,
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
        joinedload(Segment.subsegments),
        noload(Segment.subsegments if not details else None)
    )
    if exclude:
        segments = segments.filter(Segment.id.notin_(exclude))
    if bbox:
        polygon = from_shape(Polygon(bbox), srid=4326)
        segments = segments.filter(polygon.ST_Intersects(Segment.geometry))
    collection = list(map(lambda feat: serialize_segment(feat), segments))
    return schemas.SegmentCollection(features=collection)


def create_segment(
    db: Session, segment: schemas.SegmentCreate, user_id: int
) -> schemas.Segment:
    geometry = from_shape(
        LineString(coordinates=segment.geometry.coordinates), srid=4326
    )

    db_segment = Segment(geometry=geometry, owner_id=user_id)

    for subsegment in segment.properties.subsegments:
        db_prop = Subsegment(
            segment_id=db_segment.id, segment=db_segment, **subsegment.__dict__
        )
        db.add(db_prop)

    db.add(db_segment)
    db.commit()
    db.refresh(db_segment)
    return serialize_segment(db_segment)


def update_segment(
    db: Session, segment_id: int, segment: schemas.SegmentCreate, user_id: int
) -> schemas.Segment:
    geometry = from_shape(
        LineString(coordinates=segment.geometry.coordinates), srid=4326
    )

    db_segment = db.query(Segment).get(segment_id)

    # Write new subsegments
    subsegments_to_add = filter(
        lambda sub: sub.id is None, segment.properties.subsegments
    )
    for subsegment in subsegments_to_add:
        db_subsegment = Subsegment(
            segment_id=db_segment.id, segment=db_segment, **subsegment.__dict__
        )
        db.add(db_subsegment)

    # Remove stale subsegments
    old_ids = set(map(lambda sub: sub.id, db_segment.subsegments))
    new_ids = set(map(lambda sub: sub.id, segment.properties.subsegments))
    subsegments_to_remove = old_ids - new_ids

    for subsegment_id in subsegments_to_remove:
        db_subsegment = db.query(Subsegment).get(subsegment_id)
        db.delete(db_subsegment)

    # Update changed subsegments
    subsegments_to_update = filter(
        lambda sub: sub.id is not None, segment.properties.subsegments
    )
    for subsegment in subsegments_to_update:
        del subsegment.created_at
        del subsegment.modified_at
        db.query(Subsegment).filter(Subsegment.id == subsegment.id).update(
            subsegment.__dict__
        )

    db_segment.geometry = geometry
    db_segment.owner_id = user_id

    db.commit()
    db.refresh(db_segment)
    return serialize_segment(db_segment)


def delete_segment(db: Session, segment_id: int):
    segment = db.query(Segment).filter(Segment.id == segment_id).first()
    db.delete(segment)
    db.commit()
    return segment


def get_segment(db: Session, segment_id: int):
    segment = db.query(Segment).get(segment_id)
    return serialize_segment(segment)
