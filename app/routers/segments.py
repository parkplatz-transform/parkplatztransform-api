import time
from typing import List, Optional, Tuple

from fastapi import Depends, APIRouter, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.services import decode_jwt
from app import schemas, controllers
from app.database import get_db
from app.strings import validation

router = APIRouter()
bearer_scheme = HTTPBearer()


async def get_user_from_token(
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    try:
        return decode_jwt(token.credentials)
    except Exception as e:
        raise HTTPException(401, validation["unauthorized"])


async def verify_token(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    try:
        token_metadata = decode_jwt(token.credentials)
        assert token_metadata["exp"] > time.time()
    except Exception as e:
        raise HTTPException(401, validation["unauthorized"])


def parse_bounding_box(parameter: str) -> List[Tuple[float, float]]:
    spl = list(map(lambda n: float(n), parameter.split(",")))
    return list(zip(spl[0::2], spl[1::2]))


@router.get("/segments/", response_model=schemas.SegmentCollection)
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
    "/segments/", response_model=schemas.Segment, dependencies=[Depends(verify_token)]
)
def create_segment(
    segment: schemas.SegmentCreate,
    db: Session = Depends(get_db),
    token=Depends(get_user_from_token),
):
    email = token["sub"]
    created_recording = controllers.create_segment(db=db, segment=segment, email=email)
    return created_recording


@router.delete(
    "/segments/{segment_id}", response_model=int, dependencies=[Depends(verify_token)]
)
def delete_segment(segment_id: int, db: Session = Depends(get_db)):
    result = controllers.delete_segment(db=db, segment_id=segment_id)
    if not result:
        HTTPException(status_code=404)
    return segment_id


@router.put(
    "/segments/{segment_id}",
    response_model=schemas.SegmentUpdate,
    dependencies=[Depends(verify_token)],
)
def update_segment(
    segment_id: int,
    segment: schemas.SegmentUpdate,
    db: Session = Depends(get_db),
    token=Depends(get_user_from_token),
):
    email = token["sub"]
    result = controllers.update_segment(
        db=db, segment_id=segment_id, segment=segment, email=email
    )
    if not result:
        HTTPException(status_code=404)
    return result
