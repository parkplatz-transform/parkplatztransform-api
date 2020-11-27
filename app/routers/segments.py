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
async def read_segments(bbox: Optional[str] = None, db: Session = Depends(get_db)):
    if bbox:
        bbox = parse_bounding_box(bbox)
    db_recordings = controllers.get_segments(db, bbox=bbox)
    return db_recordings


@router.post(
    "/segments/", response_model=schemas.Segment, dependencies=[Depends(verify_token)]
)
def create_segment(
        segment: schemas.SegmentCreate,
        db: Session = Depends(get_db),
        token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    email = decode_jwt(token.credentials)["sub"]
    created_recording = controllers.create_segment(db=db, segment=segment, email=email)
    return created_recording


@router.delete("/segments/{segment_id}")
def delete_segment(segment_id: int, db: Session = Depends(get_db)):
    result = controllers.delete_segment(db=db, segment_id=segment_id)
    if not result:
        HTTPException(status_code=404)
    return segment_id
