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
    for subsegment in segment.properties.subsegments:
        if subsegment.parking_allowed:
            db_prop = SubsegmentParking(
                segment_id=db_segment.id, subsegment=subsegment
            )
            db.add(db_prop)
        else:
            db_prop = SubsegmentNonParking(
                segment_id=db_segment.id, subsegment=subsegment
            )
            db.add(db_prop)
    
    db.commit()
    return serialize_segment(db_segment)


def update_segment(
    db: Session, segment_id: str, segment: schemas.SegmentCreate, user_id: str
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
        if subsegment.parking_allowed:
            db_subsegment = SubsegmentParking(
                segment_id=db_segment.id, subsegment=subsegment
            )
        else:
            db_subsegment = SubsegmentNonParking(
                segment_id=db_segment.id, subsegment=subsegment
            )
        db.add(db_subsegment)

    # Remove stale subsegments
    old_ids = set(map(lambda sub: sub.id, db_segment.subsegments_non_parking + db_segment.subsegments_parking))
    new_ids = set(map(lambda sub: sub.id, segment.properties.subsegments))
    subsegments_to_remove = old_ids - new_ids

    for subsegment_id in subsegments_to_remove:
        db_subsegment
        try:
            db_subsegment = db.query(SubsegmentParking).get(subsegment_id)
        except:
            db_subsegment = db.query(SubsegmentNonParking).get(subsegment_id)
        
        db.delete(db_subsegment)

    # Update changed subsegments
    subsegments_to_update = filter(
        lambda sub: sub.id is not None, segment.properties.subsegments
    )
    for idx, subsegment in enumerate(subsegments_to_update):
        if subsegment.parking_allowed:
            db.query(SubsegmentParking).filter(SubsegmentParking.id == subsegment.id).update(
                {
                    'order_number': idx,
                    'length_in_meters': subsegment.length_in_meters,
                    'car_count': subsegment.car_count,
                    'quality': subsegment.quality,
                    'fee': subsegment.fee,
                    'street_location': subsegment.street_location,
                    'marked': subsegment.marked,
                    'alignment': subsegment.alignment,
                    'user_restrictions': subsegment.user_restrictions,
                    'alternative_usage_reason': subsegment.alternative_usage_reason,
                    'time_constraint': subsegment.time_constraint,
                    'time_constraint_reason': subsegment.time_constraint_reason,
                    'duration_constraint': subsegment.duration_constraint,
                    'duration_constraint_reason': subsegment.duration_constraint_reason,
                },
                synchronize_session=False
            )
        else:
            db.query(SubsegmentNonParking).filter(SubsegmentNonParking.id == subsegment.id).update(
                {
                    'order_number': idx,
                    'length_in_meters': subsegment.length_in_meters,
                    'quality': subsegment.quality,
                    'no_parking_reasons': subsegment.no_parking_reasons,
                },
                synchronize_session=False
            )

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
