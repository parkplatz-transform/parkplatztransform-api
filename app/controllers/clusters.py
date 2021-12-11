from typing import List, Tuple

from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from sqlalchemy.future import select
from geoalchemy2.shape import from_shape
from shapely.geometry import Polygon

from .. import schemas
from ..models import Cluster

async def fetch_clusters(
    db: Session,
    bbox: List[Tuple[float, float]]
) -> str:
    sql = """
    --begin-sql
    SELECT json_build_object(
        'type', 'FeatureCollection',
        'features', json_agg(
            json_build_object(
                'id', c.id,
                'type', 'Feature',
                'geometry', geometry,
                'bbox', json_build_array(
                    ST_XMin(geometry),
                    ST_XMax(geometry),
                    ST_YMin(geometry),
                    ST_YMax(geometry)
                ),
                'properties', json_build_object(
                  'name', c.name,
                  'label', '~' || c.count || ' ' || 'Parkplatz'
	            )
            )
        )
    ) FROM clusters c WHERE c.count > 0;
    """

    params = {
        "bbox": bbox
    }

    query = await db.execute(text(sql), params)
    return query.fetchone()[0]

async def get_clusters(
    db: Session,
    bbox: List[Tuple[float, float]] = None,
) -> schemas.ClusterCollection:
    query = select(Cluster)
    if bbox:
        polygon = from_shape(Polygon(bbox), srid=4326)
        query = query.where(polygon.ST_Intersects(Cluster.geometry))

    results = await db.execute(query)
    clusters = results.scalars().all() or []
    return schemas.ClusterCollection(features=clusters)