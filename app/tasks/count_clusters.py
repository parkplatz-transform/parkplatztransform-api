import json
import uuid
import time

from sqlalchemy.orm.session import Session

from sqlalchemy.sql import text

count_sql = """
    --begin-sql
    SELECT sum((SELECT count(subsegments_parking.car_count)
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
    VALUES (:count, ST_SetSRID(ST_GeomFromGeoJSON(:polygon), 4326), :id, :name)
    --end-sql
"""


async def count_clusters(db=Session):
    start = time.time()
    with open('app/tasks/berlin_ortsteile.geojson') as json_file:
        await db.execute(
            text('DELETE FROM clusters')
        )
        data = json.load(json_file)
        clusters = []
        for feature in data['features']:
            geom = json.dumps(feature['geometry'])
            name = feature['properties']['name']
            count_result = await db.execute(
                text(count_sql), {'polygon': geom}
            )
            count = count_result.fetchone()[0]
            clusters.append({
                'polygon': geom,
                'count': count,
                'name': name,
                'id': uuid.uuid4().hex
            })
        await db.execute(
            text(insert_sql),
            clusters
        )
        await db.commit()
        end = time.time()
        print(f"Finished cluster count in {end - start}")
