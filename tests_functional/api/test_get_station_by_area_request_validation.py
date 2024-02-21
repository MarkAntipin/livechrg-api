import os

import asyncpg
from fastapi.testclient import TestClient


async def test_get_stations_by_area__invalid_lat__returns_422(client: TestClient, pg: asyncpg.Pool) -> None:
    # arrange

    # act
    resp = client.get(
        '/api/v1/stations-by-area',
        params={
            'ne_lat': 1,
            'ne_lon': 1,
            'sw_lat': -100,
            'sw_lon': 0,
        },
        headers={
            'Authorization': os.environ['ADMIN_AUTH_TOKEN']
        }
    )

    # assert
    assert resp.status_code == 422


async def test_get_stations_by_area__invalid_lon__returns_422(client: TestClient, pg: asyncpg.Pool) -> None:
    # arrange

    # act
    resp = client.get(
        '/api/v1/stations-by-area',
        params={
            'ne_lat': 1,
            'ne_lon': 1,
            'sw_lat': 0,
            'sw_lon': -200,
        },
        headers={
            'Authorization': os.environ['ADMIN_AUTH_TOKEN']
        }
    )

    # assert
    assert resp.status_code == 422


async def test_get_stations_by_area__sw_greater_than_ne__returns_422(client: TestClient, pg: asyncpg.Pool) -> None:
    # arrange

    # act
    resp = client.get(
        '/api/v1/stations-by-area',
        params={
            'ne_lat': 0,
            'ne_lon': 0,
            'sw_lat': 10,
            'sw_lon': 10,
        },
        headers={
            'Authorization': os.environ['ADMIN_AUTH_TOKEN']
        }
    )

    # assert
    assert resp.status_code == 422
