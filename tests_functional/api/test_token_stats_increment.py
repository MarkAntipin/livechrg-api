import asyncpg
from fastapi.testclient import TestClient

from tests_functional.helpers import add_token, get_token_stats


async def test_get_stations_by_area_twice__token_stats_increment_twice(client: TestClient, pg: asyncpg.Pool) -> None:
    # arrange
    api_key = 'another_one'
    await add_token(pg=pg, api_key=api_key)

    # act
    resp = client.get(
        '/api/v1/stations',
        headers={
            'api-key': api_key,
        },
        params={
            'ne_lat': 2,
            'ne_lon': 2,
            'sw_lat': 1,
            'sw_lon': 1,
        }
    )

    # assert
    assert resp.status_code == 200

    # act
    resp = client.get(
        '/api/v1/stations',
        headers={
            'api-key': api_key,
        },
        params={
            'ne_lat': 2,
            'ne_lon': 2,
            'sw_lat': 1,
            'sw_lon': 1,
        }
    )

    # assert
    assert resp.status_code == 200

    token_stats = await get_token_stats(pg=pg, api_key=api_key)
    assert token_stats == 2
