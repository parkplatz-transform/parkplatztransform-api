from typing import List, Optional, Tuple

from fastapi import Depends, APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app import controllers
from app.services import get_db
from app.strings import validation
from app.tasks import count_clusters


router = APIRouter()


@router.get(
    "/clusters/",
    response_class=PlainTextResponse,
)
async def read_clusters(
    bbox: Optional[str] = None,
    db: Session = Depends(get_db),
):
    def parse_bounding_box(parameter: str) -> List[Tuple[float, float]]:
        spl = list(map(lambda n: float(n), parameter.split(",")))
        return list(zip(spl[0::2], spl[1::2]))

    if bbox:
        try:
            bbox = parse_bounding_box(bbox)
            assert len(bbox) >= 5
        except Exception:
            raise HTTPException(400, validation["bbox"])
    clusters = await controllers.get_clusters(db, bbox=bbox)
    headers = {"cache-control": "max-age=3600", "content-type": "application/json"}
    return PlainTextResponse(content=clusters, headers=headers)


@router.get("/clusters/count", response_class=PlainTextResponse)
def count_clusters_task(background_tasks: BackgroundTasks):
    background_tasks.add_task(
        count_clusters
    )
    return PlainTextResponse(content="OK")
