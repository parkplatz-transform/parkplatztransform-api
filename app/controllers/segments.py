from datetime import datetime
from typing import List, Tuple, Optional
from uuid import uuid4

from .. import schemas
from ..models import SubsegmentNonParking, SubsegmentParking
from ..permissions import user_can_operate
from ..services import db

segment_collection = db['segments']


async def query_segments(
    bbox: List[Tuple[float, float]],
    exclude_ids: List[str] = [],
    include_if_modified_after: Optional[datetime] = None,
) -> dict:
    features = []
    async for feature in segment_collection.find({
        'geometry': {
            '$geoIntersects': {
                '$geometry': {
                    'type': "Polygon" ,
                    'coordinates': [bbox]
                }
            }
        }
    }):
        feature['properties']['has_subsegments'] = len(
            feature['properties']['subsegments']
        ) > 0
        feature['properties']['subsegments'] = []
        feature['id'] = feature['_id']
        features.append(feature)
    return {
        'type': 'FeatureCollection',
        'features': features
    }


async def get_segment(segment_id: str):
    segment = await segment_collection.find_one({'_id' : segment_id})
    segment['id'] = segment['_id']
    segment['properties']['has_subsegments'] = len(
            segment['properties']['subsegments']
        ) > 0
    return segment


async def get_segments() -> dict:
    features = []
    async for feature in segment_collection.find():
        features.append(feature)
    return {
        'type': 'FeatureCollection',
        'features': features
    }


def create_subsegments(subsegments, segment_id: str):
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
    segment: dict, user_id: str
) -> dict:
    segment['_id'] = str(uuid4())
    segment['properties']['created_at'] = datetime.now()
    segment['properties']['modified_at'] = datetime.now()
    segment['properties']['owner_id'] = user_id

    result = await segment_collection.insert_one(segment)

    if result.acknowledged is True:
        segment['id'] = segment['_id']
        return segment


async def update_segment(
    segment_id: str, segment: dict, user: schemas.User
) -> dict:
    db_segment = await segment_collection.find_one({'_id': segment_id})
    user_can_operate(user, db_segment['properties']['owner_id'])

    segment['properties']['owner_id'] = user['id']
    await segment_collection.replace_one(
        {'_id': segment_id},
        segment
    )
    updated_segment = await segment_collection.find_one({'_id': segment_id})
    updated_segment['id'] = updated_segment['_id']
    return updated_segment


async def delete_segment(segment_id: str, user: schemas.User):
    segment = await segment_collection.find_one({'_id': segment_id})
    # Send a 403 and bail out if the user does not have appropriate permissions
    user_can_operate(user, segment['properties']['owner_id'])
    await segment_collection.delete_one({'_id': segment_id})
    return True
