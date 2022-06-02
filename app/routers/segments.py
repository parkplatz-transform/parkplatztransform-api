import datetime
from typing import List, Optional, Tuple

from fastapi import Depends, APIRouter, HTTPException, WebSocket, Request, Response
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app import schemas, controllers
from app.services import get_db
from app.strings import validation
from app.routers.users import get_session

router = APIRouter()


def parse_bounding_box(parameter: str) -> str:
    bounds = ",".join(" ".join(s) for s in zip(*[iter(parameter.split(","))] * 2))
    return f"SRID=4326;POLYGON(({bounds}))"


@router.post(
    "/query-segments/",
    response_class=PlainTextResponse,
)
async def query_segments(
    body: schemas.SegmentQuery,
    db: Session = Depends(get_db),
):
    bbox = parse_bounding_box(body.bbox)
    result = await controllers.query_segments(
        db=db,
        bbox=bbox,
        exclude_ids=body.exclude_ids,
        include_if_modified_after=body.include_if_modified_after,
    )
    headers = headers = {"content-type": "application/json"}
    return PlainTextResponse(content=result, headers=headers)


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    db: Session = Depends(get_db),
):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        bbox = parse_bounding_box(data["bbox"])
        result = await controllers.query_segments(
            db=db,
            bbox=bbox,
            exclude_ids=data["exclude_ids"],
        )

        await websocket.send_text(result)


@router.get(
    "/segments/",
    response_model=schemas.SegmentCollection,
)
async def read_segments(
    bbox: Optional[str] = None,
    modified_after: Optional[str] = None,
    details: bool = True,
    db: Session = Depends(get_db),
):
    def parse_bounding_box(parameter: str) -> List[Tuple[float, float]]:
        spl = list(map(lambda n: float(n), parameter.split(",")))
        return list(zip(spl[0::2], spl[1::2]))

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
    db_segments = await controllers.get_segments(
        db, bbox=bbox, modified_after=modified_after, details=details
    )
    return db_segments


@router.get(
    "/segments/{segment_id}/",
    response_model=schemas.Segment,
)
async def read_segment(
    segment_id: str, request: Request, response: Response, db: Session = Depends(get_db)
):
    segment = await controllers.get_segment(db=db, segment_id=segment_id)
    last_updated_pattern = "%a, %d %b %Y %H:%M:%S GMT"
    last_modified = datetime.datetime.fromisoformat(
        segment.properties["modified_at"]
    ).replace(microsecond=0)

    if request.headers.get("if-modified-since"):
        if_modified = datetime.datetime.strptime(
            request.headers.get("if-modified-since"), last_updated_pattern
        )
        if if_modified == last_modified:
            return Response(status_code=304)

    response.headers["last-modified"] = last_modified.strftime(last_updated_pattern)

    if not segment:
        HTTPException(status_code=404)
    return segment


@router.post(
    "/segments/", response_model=schemas.Segment, dependencies=[Depends(get_session)]
)
async def create_segment(
    segment: schemas.SegmentCreate,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_session),
):
    return await controllers.create_segment(db=db, segment=segment, user_id=user.id)


@router.delete(
    "/segments/{segment_id}/", response_model=str, dependencies=[Depends(get_session)]
)
async def delete_segment(
    segment_id: str,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_session),
):
    result = await controllers.delete_segment(db=db, segment_id=segment_id, user=user)
    if not result:
        HTTPException(status_code=404)
    return segment_id


@router.put(
    "/segments/{segment_id}/",
    response_model=schemas.Segment,
    dependencies=[Depends(get_session)],
)
async def update_segment(
    segment_id: str,
    segment: schemas.SegmentUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_session),
):
    result = await controllers.update_segment(
        db=db, segment_id=segment_id, segment=segment, user=user
    )
    if not result:
        HTTPException(status_code=404)
    return result
