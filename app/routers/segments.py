import time
from typing import List, Optional, Tuple

from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session

from app import schemas, controllers
from app.database import get_db
from app.strings import validation
from app.sessions import get_session

router = APIRouter()


def parse_bounding_box(parameter: str) -> List[Tuple[float, float]]:
    spl = list(map(lambda n: float(n), parameter.split(",")))
    return list(zip(spl[0::2], spl[1::2]))


@router.get("/segments/",  response_model=schemas.SegmentCollection)
async def read_segments(
    bbox: Optional[str] = None,
    exclude: Optional[str] = None,
    details: bool = True,
    db: Session = Depends(get_db),
):
    if exclude:
        try:
            exclude = exclude.split(",")
        except Exception as e:
            raise HTTPException(400, validation["exclude"])
    if bbox:
        try:
            bbox = parse_bounding_box(bbox)
            assert len(bbox) >= 5
        except Exception as e:
            raise HTTPException(400, validation["bbox"])
    db_recordings = controllers.get_segments(
        db, bbox=bbox, exclude=exclude, details=details
    )
    return db_recordings


@router.get(
    "/segments/{segment_id}",
    response_model=schemas.Segment,
)
def read_segment(segment_id: int, db: Session = Depends(get_db)):
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
    created_recording = controllers.create_segment(db=db, segment=segment, user_id=user.id)
    return created_recording


@router.delete(
    "/segments/{segment_id}", response_model=int, dependencies=[Depends(get_session)]
)
def delete_segment(segment_id: int, db: Session = Depends(get_db)):
    result = controllers.delete_segment(db=db, segment_id=segment_id)
    if not result:
        HTTPException(status_code=404)
    return segment_id


@router.put(
    "/segments/{segment_id}",
    response_model=schemas.Segment,
    dependencies=[Depends(get_session)],
)
def update_segment(
    segment_id: int,
    segment: schemas.SegmentUpdate,
    db: Session = Depends(get_db),
    session=Depends(get_session),
):
    result = controllers.update_segment(
        db=db, segment_id=segment_id, segment=segment, user_id=session.id
    )
    if not result:
        HTTPException(status_code=404)
    return result
