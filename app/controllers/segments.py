from datetime import datetime
from typing import List, Tuple, Optional

from sqlalchemy.orm import Session, joinedload, noload
from sqlalchemy.sql import or_
from sqlalchemy.future import select
from geoalchemy2.shape import from_shape
from shapely.geometry import Polygon, shape
from sqlalchemy import update

from .. import schemas
from ..models import Segment, SubsegmentNonParking, SubsegmentParking
from ..permissions import user_can_operate


async def query_segments(
    db: Session,
    bbox: List[Tuple[float, float]],
    details: bool = True,
    exclude_ids: List[str] = [],
    include_if_modified_after: Optional[datetime] = None,
) -> schemas.SegmentCollection:
    polygon = from_shape(Polygon(bbox), srid=4326)
    if include_if_modified_after:
        segment_filter = or_(
            Segment.id.notin_(exclude_ids),
            Segment.modified_at > include_if_modified_after,
        )
    else:
        segment_filter = Segment.id.notin_(exclude_ids)

    query = await db.execute((
        select(Segment)
        .where(segment_filter)
        .where(polygon.ST_Intersects(Segment._geometry))
        .options(
            noload(Segment.subsegments_parking if not details else None),
            noload(Segment.subsegments_non_parking if not details else None),
        )
    ))
    segments = query.scalars().all()
    return {'features': segments}


async def get_segment(db: Session, segment_id: str):
    query = await db.execute((
        select(Segment)
        .where(Segment.id == segment_id)
    ))
    segment = query.scalars().first()
    return segment


async def get_segments(
    db: Session,
    bbox: List[Tuple[float, float]] = None,
    modified_after: Optional[datetime] = None,
    details: bool = True,
) -> schemas.SegmentCollection:
    query = select(Segment).options(
        joinedload(Segment.subsegments_parking),
        joinedload(Segment.subsegments_non_parking),
        noload(Segment.subsegments_parking if not details else None),
        noload(Segment.subsegments_non_parking if not details else None),
    )
    if modified_after:
        query = query.where(Segment.modified_at > modified_after)
    if bbox:
        polygon = from_shape(Polygon(bbox), srid=4326)
        query = query.where(polygon.ST_Intersects(Segment._geometry))

    results = await db.execute(query)
    segments = results.unique().scalars().all() or []
    return schemas.SegmentCollection(features=segments)


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


async def create_segment(
    db: Session, segment: schemas.SegmentCreate, user_id: str
) -> schemas.Segment:
    geometry = from_shape(shape(segment.geometry), srid=4326)

    db_segment = Segment()
    db_segment.further_comments = segment.properties.further_comments
    db_segment.data_source = segment.properties.data_source
    db_segment._geometry = geometry
    db_segment.owner_id = user_id

    db.add(db_segment)

    await db.commit()
    await db.flush()
    await db.refresh(db_segment)
    create_subsegments(db, segment.properties.subsegments, db_segment.id)

    await db.refresh(db_segment)

    return db_segment


async def update_segment(
    db: Session, segment_id: str, segment: schemas.SegmentCreate, user: schemas.User
) -> schemas.Segment:
    geometry = from_shape(shape(segment.geometry), srid=4326)

    db_segment = await get_segment(db, segment_id)
    query = update(Segment).where(Segment.id == segment_id)

    # Send a 403 and bail out if the user does not have appropriate permissions
    user_can_operate(user, db_segment.owner_id)

    delete_parking = SubsegmentParking.__table__.delete().where(
        SubsegmentParking.segment_id == segment_id
    )
    delete_non_parking = SubsegmentNonParking.__table__.delete().where(
        SubsegmentNonParking.segment_id == segment_id
    )
    await db.execute(delete_parking)
    await db.execute(delete_non_parking)

    create_subsegments(db, segment.properties.subsegments, segment_id)

    query = query.values(
        _geometry=geometry,
        data_source=segment.properties.data_source,
        further_comments=segment.properties.further_comments,
        # Always changes to the last user who edited the segment
        owner_id=user.id
    )
    await db.execute(query)
    await db.commit()
    await db.flush()
    await db.refresh(db_segment)
    return db_segment


async def delete_segment(db: Session, segment_id: str, user: schemas.User):
    segment = await get_segment(db, segment_id)
    # Send a 403 and bail out if the user does not have appropriate permissions
    user_can_operate(user, segment.owner_id)
    await db.delete(segment)
    await db.commit()
    return await db.flush()
