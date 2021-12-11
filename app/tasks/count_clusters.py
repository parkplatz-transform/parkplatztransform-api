import json
import uuid

from app.services import engine
from sqlalchemy.sql import text

count_sql = """
    --begin-sql
    SELECT count((SELECT count(subsegments_parking.car_count)
    FROM subsegments_parking
    WHERE subsegments_parking.segment_id = segments.id))
    FROM segments
    WHERE ST_Intersects(
        ST_SetSRID(ST_GeomFromGeoJSON(:polygon), 4326), 
        segments.geometry
    )
    --end-sql
"""


insert_sql = """
    --begin-sql
    INSERT INTO clusters (count, geometry, id, name)
    VALUES (:count, :polygon, :id, :name)
    --end-sql
"""


async def count_clusters():
    async with engine.begin() as conn:
        with open('app/tasks/berlin_ortsteile.geojson') as json_file:
            await conn.execute(
                text('DELETE FROM clusters')
            )
            data = json.load(json_file)
            for feature in data['features']:
                geom = json.dumps(feature['geometry'])
                name = feature['properties']['name']
                count_result = await conn.execute(
                    text(count_sql), {'polygon': geom}
                )
                count = count_result.fetchone()[0]
                await conn.execute(
                    text(insert_sql),
                    {
                        'polygon': geom,
                        'count': count,
                        'name': name,
                        'id': uuid.uuid4().hex
                    }
                )
