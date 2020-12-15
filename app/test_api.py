import base64
import json

from fastapi.testclient import TestClient

from app.main import app
from app.routers.segments import verify_token, get_user_from_token
from app.services import OneTimeAuth


client = TestClient(app)

OTA = OneTimeAuth()
email = "testuser@email.com"
token = OTA.generate_token(email)


def get_user_from_token_mock():
    return {
        "sub": email
    }


def verify_token_mock():
    return True


app.dependency_overrides[get_user_from_token] = get_user_from_token_mock
app.dependency_overrides[verify_token] = verify_token_mock


def test_create_user():
    response = client.get(f"/users/verify/?code={token}&email={email}")
    assert response.status_code == 200
    assert response.json() == {
        "access_token": base64.b64decode(token).decode("utf8"),
        "token_type": "Bearer"
    }


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
    assert response.json()["geometry"] == data["geometry"]


def test_read_segments_with_bbox():
    response = client.get(
        "/segments/?bbox=13.431708812713623,52.547078621160054,\
        13.435056209564207,52.547078621160054,\
        13.435056209564207,52.548370414628614,\
        13.431708812713623,52.548370414628614,\
        13.431708812713623,52.547078621160054"
    )
    assert response.status_code == 200
    assert len(response.json()["features"]) == 1
    assert response.json()["features"][0]["geometry"]["coordinates"] == [[
            13.43244105577469,
            52.54816979768233
        ],
        [
            13.43432933092117,
            52.54754673757979
        ]
    ]
