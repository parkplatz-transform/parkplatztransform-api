import uuid
import json

from fastapi.testclient import TestClient

from app.main import app
from app.sessions import get_session, SessionStorage
from app.schemas import User
from app.services import OneTimeAuth


client = TestClient(app)

OTA = OneTimeAuth()
email = "testuser@email.com"
token = OTA.generate_token(email)

user_id = uuid.uuid4().hex


def get_session_mock():
    return User(id=user_id, email=email, permission_level=0)


class SessionStorageMock:
    async def create_session(self, user: User):
        return {}


app.dependency_overrides[get_session] = get_session_mock
app.dependency_overrides[SessionStorage] = SessionStorageMock


def test_docs():
    response = client.get("docs")
    assert response.status_code == 200


def test_create_user():
    client.get(f"/users/verify/?code={token}&email={email}")
    response = client.get("/users/me")
    assert response.status_code == 200


def test_create_segment():
    data = {
        "type": "Feature",
        "properties": {
            "subsegments": [
                {
                    "parking_allowed": True,
                    "order_number": 0,
                    "length_in_meters": 0,
                    "car_count": 0,
                    "quality": 1,
                    "fee": False,
                    "street_location": "street",
                    "marked": False,
                    "alignment": "parallel",
                    "duration_constraint": False,
                    "user_restrictions": "handicap",
                    "time_constraint": False,
                    "time_constraint_reason": "string",
                    "no_parking_reasons": [],
                }
            ]
        },
        "geometry": {
            "coordinates": [
                [13.43244105577469, 52.54816979768233],
                [13.43432933092117, 52.54754673757979],
            ],
            "type": "LineString",
        },
    }
    response = client.post("/segments/", json.dumps(data))
    assert response.status_code == 200
    assert response.json()["geometry"]["coordinates"] == data["geometry"]["coordinates"]
    assert response.json()["geometry"]["type"] == data["geometry"]["type"]
    assert len(response.json()["properties"]["subsegments"]) == 1


def test_read_segments_with_options():
    response = client.get("/segments")
    assert response.status_code == 200
    assert len(response.json()["features"]) == 1

    response = client.get("/segments/?details=0")
    assert response.status_code == 200
    assert response.json()["features"][0]["properties"]["subsegments"] == []

    response = client.get("/segments/?exclude=1")
    assert response.status_code == 200
    assert response.json()["features"] == []


def test_read_segments_with_bbox():
    # Test inside
    response = client.get(
        "/segments/?bbox=13.431708812713623,52.547078621160054,\
        13.435056209564207,52.547078621160054,\
        13.435056209564207,52.548370414628614,\
        13.431708812713623,52.548370414628614,\
        13.431708812713623,52.547078621160054"
    )
    assert response.status_code == 200
    assert len(response.json()["features"]) == 1
    assert response.json()["features"][0]["geometry"]["coordinates"] == [
        [13.43244105577469, 52.54816979768233],
        [13.43432933092117, 52.54754673757979],
    ]

    # Test outside
    response = client.get(
        "/segments/?bbox=13.438317775726318,52.546367466104385,\
        13.450162410736084,52.546367466104385,\
        13.450162410736084,52.552030289646375,\
        13.438317775726318,52.552030289646375,\
        13.438317775726318,52.546367466104385"
    )
    assert response.status_code == 200
    assert response.json() == {
        "bbox": None,
        "features": [],
        "type": "FeatureCollection",
    }


def test_read_segments_with_exclude():
    response = client.get("/segments/?exclude=1")
    assert response.status_code == 200
    assert response.json() == {
        "bbox": None,
        "features": [],
        "type": "FeatureCollection",
    }


def test_read_segment():
    response = client.get("/segments/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["geometry"]["coordinates"] == [
        [13.43244105577469, 52.54816979768233],
        [13.43432933092117, 52.54754673757979],
    ]


def test_update_segment():
    data = {
        "type": "Feature",
        "properties": {
            "subsegments": [
                {
                    "id": 1,
                    "parking_allowed": True,
                    "order_number": 0,
                    "length_in_meters": 0,
                    "car_count": 0,
                    "quality": 1,
                    "fee": False,
                    "street_location": "street",
                    "marked": True,
                    "alignment": "parallel",
                    "duration_constraint": False,
                    "user_restrictions": "handicap",
                    "alternative_usage_reason": "market",
                    "time_constraint": False,
                    "time_constraint_reason": "string",
                    "no_parking_reasons": [],
                },
                # Add a subsegment
                {
                    "parking_allowed": False,
                    "order_number": 0,
                    "length_in_meters": 0,
                    "car_count": 0,
                    "quality": 1,
                    "fee": False,
                    "street_location": "unknown",
                    "marked": False,
                    "alignment": "parallel",
                    "duration_constraint": False,
                    "user_restrictions": None,
                    "time_constraint": False,
                    "time_constraint_reason": "string",
                    "no_parking_reasons": ["private_parking"],
                },
            ]
        },
        "geometry": {
            "coordinates": [
                [13.43244105577469, 52.54816979768233],
                [13.43432933092117, 52.54754673757970],
            ],
            "type": "LineString",
        },
    }
    response = client.put("/segments/1", json.dumps(data))
    print(response.json())
    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["geometry"]["coordinates"] == data["geometry"]["coordinates"]
    assert response.json()["geometry"]["type"] == data["geometry"]["type"]
    assert len(response.json()["properties"]["subsegments"]) == 2
    assert response.json()["properties"]["subsegments"][0]["marked"]
    assert response.json()["properties"]["subsegments"][1]["street_location"] is None
    assert (
        response.json()["properties"]["subsegments"][0]["user_restrictions"]
        == "handicap"
    )
    assert (
        response.json()["properties"]["subsegments"][0]["alternative_usage_reason"]
        == "market"
    )
    assert response.json()["properties"]["subsegments"][1]["no_parking_reasons"] == [
        "private_parking"
    ]


def test_delete_segment():
    response = client.delete("/segments/1")
    assert response.status_code == 200
