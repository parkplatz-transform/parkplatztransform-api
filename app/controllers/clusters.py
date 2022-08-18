from ..services import db

cluster_collection = db['clusters']


async def get_clusters() -> dict:
    clusters = []
    async for cluster in cluster_collection.find():
        cluster['properties'] = {}
        cluster['properties']['name'] = cluster['name']
        clusters.append(cluster)
    return {
        'type': 'FeatureCollection',
        'features': clusters
    }
