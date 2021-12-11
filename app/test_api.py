import uuid
import datetime
import pytest
from unittest.mock import patch

from fastapi.testclient import TestClient
from httpx import AsyncClient
import asyncio

from app.main import app
from app.sessions import get_session, SessionStorage
from app.schemas import User
from app.services import OneTimeAuth


client = TestClient(app)

OTA = OneTimeAuth()
email = "testuser@email.com"
token = OTA.generate_token(email)


@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


def pytest_namespace():
    return {
        "segment_id": None,
        "subsegment_id": None,
    }


user_id = uuid.UUID("2873b1fb-abc3-4e9d-bfce-a65453fce811")


def get_session_mock():
    return User(id=user_id.hex, email=email, permission_level=1)


class SessionStorageMock:
    async def create_session(self, user: User):
        return {}


app.dependency_overrides[get_session] = get_session_mock
app.dependency_overrides[SessionStorage] = SessionStorageMock


@pytest.mark.asyncio
async def test_docs():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/docs")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_user():
    with patch.object(uuid, "uuid4", side_effect=lambda: user_id):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            await ac.get(f"/users/verify/?code={token}&email={email}")
            response = await ac.get("/users/me/")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_segment():
    data = {
        "type": "Feature",
        "properties": {
            "data_source": "example data source",
            "further_comments": "extra comments",
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
            ],
        },
        "geometry": {
            "coordinates": [
                [13.43244105577469, 52.54816979768233],
                [13.43432933092117, 52.54754673757979],
            ],
            "type": "LineString",
        },
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/segments/", json=data)
        pytest.segment_id = response.json()["id"]
    assert response.status_code == 200
    assert response.json()["geometry"]["coordinates"] == data["geometry"]["coordinates"]
    assert response.json()["geometry"]["type"] == data["geometry"]["type"]
    assert response.json()["properties"]["further_comments"] == "extra comments"
    assert response.json()["properties"]["data_source"] == "example data source"
    assert len(response.json()["properties"]["subsegments"]) == 1


@pytest.mark.asyncio
async def test_create_segment_polygon():
    data = {
        "type": "Feature",
        "properties": {
            "data_source": "example data source",
            "further_comments": "extra comments",
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
            ],
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [13.417729139328003, 52.59056764985919],
                    [13.419644236564636, 52.590919611743644],
                    [13.419198989868164, 52.5913367480942],
                    [13.417326807975769, 52.59061001579123],
                    [13.417729139328003, 52.59056764985919],
                ]
            ],
        },
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/segments/", json=data)
    assert response.status_code == 200
    assert response.json()["geometry"]["type"] == data["geometry"]["type"]
    assert response.json()["properties"]["further_comments"] == "extra comments"
    assert response.json()["properties"]["data_source"] == "example data source"
    assert len(response.json()["properties"]["subsegments"]) == 1


@pytest.mark.asyncio
async def test_read_segments_with_options():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/segments/")
        assert response.status_code == 200
        assert len(response.json()["features"]) == 2

        response = await ac.get("/segments/?details=0")
        assert response.status_code == 200
        assert response.json()["features"][0]["properties"]["subsegments"] == []

        response = await ac\
            .get(f"/segments/?modified_after={datetime.datetime.utcnow()}")
        assert response.status_code == 200
        assert response.json()["features"] == []


@pytest.mark.asyncio
async def test_read_segments_with_bbox():
    # Test inside
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
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
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
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


@pytest.mark.asyncio
async def test_read_segment():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"/segments/{pytest.segment_id}/")
    assert response.status_code == 200
    assert response.json()["id"] == pytest.segment_id
    assert response.json()["geometry"]["coordinates"] == [
        [13.43244105577469, 52.54816979768233],
        [13.43432933092117, 52.54754673757979],
    ]


@pytest.mark.asyncio
async def test_update_segment():
    data = {
        "type": "Feature",
        "properties": {
            "data_source": "updated data source",
            "further_comments": "updated extra comments",
            "subsegments": [
                {
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
                    "user_restriction": True,
                    "user_restriction_reason": "handicap",
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
                    "street_location": None,
                    "marked": False,
                    "alignment": "parallel",
                    "duration_constraint": False,
                    "user_restriction": None,
                    "time_constraint": False,
                    "time_constraint_reason": "string",
                    "no_parking_reasons": ["private_parking"],
                },
            ],
        },
        "geometry": {
            "coordinates": [
                [13.43244105577469, 52.54816979768233],
                [13.43432933092117, 52.54754673757970],
            ],
            "type": "LineString",
        },
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.put(f"/segments/{pytest.segment_id}/", json=data)
    assert response.status_code == 200
    assert response.json()["id"] == pytest.segment_id
    assert response.json()["geometry"]["coordinates"] == data["geometry"]["coordinates"]
    assert response.json()["geometry"]["type"] == data["geometry"]["type"]
    assert response.json()["properties"]["subsegments"][0]["marked"]
    assert response.json()["properties"]["subsegments"][1]["street_location"] is None
    assert response.json()["properties"]["subsegments"][0]["user_restriction"]
    assert response.json()["properties"]["further_comments"] == "updated extra comments"
    assert response.json()["properties"]["data_source"] == "updated data source"
    assert (
        response.json()["properties"]["subsegments"][0]["user_restriction_reason"]
        == "handicap"
    )
    assert (
        response.json()["properties"]["subsegments"][0]["alternative_usage_reason"]
        == "market"
    )
    assert response.json()["properties"]["subsegments"][1]["no_parking_reasons"] == [
        "private_parking"
    ]


@pytest.mark.asyncio
async def test_delete_segment():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete(f"/segments/{pytest.segment_id}/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_clusters():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/clusters/")
    assert response.status_code == 200
