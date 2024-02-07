import os

import asyncpg
from fastapi.testclient import TestClient

from tests_functional.helpers import add_token, get_token_stats


async def test_get_stations_by_area__with_admin_token(client: TestClient, pg: asyncpg.Pool) -> None:
    # arrange

    # act
    resp = client.get(
        '/api/v1/stations-by-area',
        params={
            'ne_lat': 2,
            'ne_lon': 2,
            'sw_lat': 1,
            'sw_lon': 1,
        },
        headers={
            'Authorization': os.environ['ADMIN_AUTH_TOKEN']
        }
    )

    # assert
    assert resp.status_code == 200


async def test_get_stations_by_area__with_client_token(client: TestClient, pg: asyncpg.Pool) -> None:
    # arrange
    sample_key = "karramba"
    await add_token(pg=pg, api_key=sample_key)
    # act
    resp = client.get(
        '/api/v1/stations-by-area',
        params={
            'ne_lat': 2,
            'ne_lon': 2,
            'sw_lat': 1,
            'sw_lon': 1,
        },
        headers={
            'Authorization': sample_key
        }
    )

    # assert
    assert resp.status_code == 200


async def test_get_stations_by_area__no_auth_token(client: TestClient, pg: asyncpg.Pool) -> None:
    # act
    resp = client.get(
        '/api/v1/stations-by-area',
        params={
            'ne_lat': 2,
            'ne_lon': 2,
            'sw_lat': 1,
            'sw_lon': 1,
        },
    )

    # assert
    assert resp.status_code == 401


async def test_get_stations_by_area__invalid_auth_token(client: TestClient, pg: asyncpg.Pool) -> None:
    # act
    resp = client.get(
        '/api/v1/stations-by-area',
        params={
            'ne_lat': 2,
            'ne_lon': 2,
            'sw_lat': 1,
            'sw_lon': 1,
        },
        headers={
            'Authorization': 'invalid_token'
        }
    )

    # assert
    assert resp.status_code == 403


async def test_get_stations_by_area_twice__token_stats_increment_twice(client: TestClient, pg: asyncpg.Pool) -> None:
    # arrange
    sample_key = "karramba"
    await add_token(pg=pg, api_key=sample_key)

    # act
    resp = client.get(
        '/api/v1/stations-by-area',
        params={
            'ne_lat': 2,
            'ne_lon': 2,
            'sw_lat': 1,
            'sw_lon': 1,
        },
        headers={
            'Authorization': sample_key
        }
    )

    # assert
    assert resp.status_code == 200

    # act
    resp = client.get(
        '/api/v1/stations-by-area',
        params={
            'ne_lat': 2,
            'ne_lon': 2,
            'sw_lat': 1,
            'sw_lon': 1,
        },
        headers={
            'Authorization': sample_key
        }
    )

    # assert
    assert resp.status_code == 200

    token_stats = await get_token_stats(pg=pg, api_key=sample_key)
    assert token_stats == 2
