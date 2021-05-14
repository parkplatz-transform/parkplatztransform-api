import datetime
from typing import List, Optional, Tuple

from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session

from app import schemas, controllers
from app.services import get_db
from app.strings import validation
from app.sessions import get_session

router = APIRouter()


def parse_bounding_box(parameter: str) -> List[Tuple[float, float]]:
    spl = list(map(lambda n: float(n), parameter.split(",")))
    return list(zip(spl[0::2], spl[1::2]))


def parse_timestamp(timestamp: Optional[str]) -> datetime:
    try:
        return datetime.datetime.fromisoformat(timestamp)
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post(
    "/query-segments",
    response_model=schemas.SegmentCollection,
)
def query_segments(
    body: schemas.SegmentQuery,
    db: Session = Depends(get_db),
):
    if body.include_if_modified_after:
        body.include_if_modified_after = parse_timestamp(body.include_if_modified_after)
    bbox = parse_bounding_box(body.bbox)
    result = controllers.query_segments(
        db=db,
        bbox=bbox,
        exclude_ids=body.exclude_ids,
        include_if_modified_after=body.include_if_modified_after,
    )
    return result


@router.get(
    "/segments/",
    response_model=schemas.SegmentCollection,
)
def read_segments(
    bbox: Optional[str] = None,
    modified_after: Optional[str] = None,
    details: bool = True,
    db: Session = Depends(get_db),
):
    if modified_after:
        try:
            modified_after = datetime.datetime.fromisoformat(modified_after)
        except Exception as e:
            raise HTTPException(400, str(e))
    if bbox:
        try:
            bbox = parse_bounding_box(bbox)
            assert len(bbox) >= 5
        except Exception:
            raise HTTPException(400, validation["bbox"])
    db_segments = controllers.get_segments(
        db, bbox=bbox, modified_after=modified_after, details=details
    )
    return db_segments


@router.get(
    "/segments/{segment_id}",
    response_model=schemas.Segment,
)
def read_segment(segment_id: str, db: Session = Depends(get_db)):
    segment = controllers.get_segment(db=db, segment_id=segment_id)
    if not segment:
        HTTPException(status_code=404)
    return segment


@router.post(
    "/segments/", response_model=schemas.Segment, dependencies=[Depends(get_session)]
)
def create_segment(
    segment: schemas.SegmentCreate,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_session),
):
    return controllers.create_segment(db=db, segment=segment, user_id=user.id)


@router.delete(
    "/segments/{segment_id}", response_model=str, dependencies=[Depends(get_session)]
)
def delete_segment(
    segment_id: str,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_session),
):
    result = controllers.delete_segment(db=db, segment_id=segment_id, user=user)
    if not result:
        HTTPException(status_code=404)
    return segment_id


@router.put(
    "/segments/{segment_id}",
    response_model=schemas.Segment,
    dependencies=[Depends(get_session)],
)
def update_segment(
    segment_id: str,
    segment: schemas.SegmentUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_session),
):
    result = controllers.update_segment(
        db=db, segment_id=segment_id, segment=segment, user=user
    )
    if not result:
        HTTPException(status_code=404)
    return result
