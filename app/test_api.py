import json

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models.base_mixin import Base
from app.routers.segments import verify_token, get_user_from_token


client = TestClient(app)


def get_user_from_token_mock():
    return {
        "sub": "testuser@email.com"
    }


def verify_token_mock():
    return True


app.dependency_overrides[get_user_from_token] = get_user_from_token_mock
app.dependency_overrides[verify_token] = verify_token_mock


def test_read_segments():
    response = client.get("/segments")
    assert response.status_code == 200
    assert response.json() == {
        'bbox': None,
        'features': [],
        'type': 'FeatureCollection'
    }


def test_create_segment():
    data = {
        "type": "Feature",
        "properties": {
            "subsegments": [
                {
                    "order_number": 0,
                    "parking_allowed": True,
                    "count": 0,
                    "marked": True,
                    "alignment": "parallel",
                    "street_location": "street",
                    "length_in_meters": 0,
                    "car_count": 0,
                    "quality": 1
                }
            ]
        },
        "geometry": {
            "coordinates": [
                [
                    13.43244105577469,
                    52.54816979768233
                ],
                [
                    13.43432933092117,
                    52.54754673757979
                ]
            ],
            "type": "LineString"
        }
    }
    response = client.post("/segments/", json.dumps(data))
    assert response.status_code == 200
