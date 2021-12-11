from typing import List, Tuple

from sqlalchemy.orm import Session
from sqlalchemy.sql import text


async def get_clusters(
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
                'geometry', ST_AsGeoJSON(geometry)::json,
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
