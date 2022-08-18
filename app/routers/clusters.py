from fastapi import APIRouter
from fastapi.responses import PlainTextResponse, ORJSONResponse

from app import controllers

router = APIRouter()


@router.get(
    "/clusters/",
    response_class=ORJSONResponse,
)
async def read_clusters():
    clusters = await controllers.get_clusters()
    return ORJSONResponse(clusters)
