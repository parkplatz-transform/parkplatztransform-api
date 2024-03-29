from fastapi import Depends, APIRouter, HTTPException, WebSocket, Request
from fastapi.responses import PlainTextResponse, ORJSONResponse

from app import schemas, controllers
from app.routers.users import get_session
from ..services import db

router = APIRouter()


@router.post(
    "/query-segments/",
    response_class=PlainTextResponse,
)
async def query_segments(
    body: schemas.SegmentQuery,
):

    result = await controllers.query_segments(
        bbox=body.bbox,
        exclude_ids=body.exclude_ids,
        include_if_modified_after=body.include_if_modified_after,
    )
    return ORJSONResponse(content=result)


@router.get(
    "/segments/",
    response_class=ORJSONResponse,
)
async def read_segments():
    db_segments = await controllers.get_segments()
    return ORJSONResponse(content=db_segments)


@router.get(
    "/segments/{segment_id}/",
    response_model=schemas.Segment,
)
async def read_segment(
    segment_id: str, request: Request, response: ORJSONResponse
):
    segment = await controllers.get_segment(segment_id=segment_id)

    if not segment:
        HTTPException(status_code=404)
    return segment


@router.post(
    "/segments/", response_class=ORJSONResponse, dependencies=[Depends(get_session)]
)
async def create_segment(
    segment: dict,
    user: dict = Depends(get_session),
):
    return await controllers.create_segment(segment=segment, user_id=user['id'])


@router.delete(
    "/segments/{segment_id}/", response_model=str, dependencies=[Depends(get_session)]
)
async def delete_segment(
    segment_id: str,
    user: schemas.User = Depends(get_session),
):
    result = await controllers.delete_segment(segment_id=segment_id, user=user)
    if not result:
        HTTPException(status_code=404)
    return segment_id


@router.put(
    "/segments/{segment_id}/",
    response_class=ORJSONResponse,
    dependencies=[Depends(get_session)],
)
async def update_segment(
    segment_id: str,
    segment: dict,
    user=Depends(get_session),
):
    result = await controllers.update_segment(
        segment_id=segment_id, segment=segment, user=user
    )
    if not result:
        HTTPException(status_code=404)
    return result
