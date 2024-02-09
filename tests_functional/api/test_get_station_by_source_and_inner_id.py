import os

import asyncpg
from fastapi.testclient import TestClient

from src.api.routers.v1.models import SourceName
from tests_functional.helpers import add_charger, add_comment, add_event, add_source, add_station


async def test_get_station_by_source_and_inner_id(client: TestClient, pg: asyncpg.Pool) -> None:
    # arrange
    station_id = await add_station(pg=pg, latitude=1.4, longitude=1.5, rating=5)
    await add_source(pg=pg, station_id=station_id, station_inner_id=1, source='plug_share')
    await add_comment(pg=pg, station_id=station_id, text='text', source='plug_share')
    await add_event(pg=pg, station_id=station_id, source='plug_share', is_problem=False)
    await add_charger(pg=pg, station_id=station_id, network='network')

    #act
    resp = client.get(
        '/api/v1/stations',
        params={
            'station_source': SourceName.plug_share.value,
            'station_inner_id': 1,
        },
        headers={
            'Authorization': os.environ['ADMIN_AUTH_TOKEN']
        }
    )

    # assert
    assert resp.status_code == 200

    station = resp.json()

    # basic fields
    assert station['coordinates']['lat'] == 1.4
    assert station['coordinates']['lon'] == 1.5
    assert station['sources']
    assert station['chargers']
    assert station['events']
    assert station['comments']

    # custom metrics fields
    assert station['average_rating'] == 5
    assert station['last_event']['is_problem'] is False


async def test_get_station_by_source_and_inner_id__not_found(client: TestClient, pg: asyncpg.Pool) -> None:
    #act
    resp = client.get(
        '/api/v1/stations',
        params={
            'station_source': 'plug_share',
            'station_inner_id': 1,
        },
        headers={
            'Authorization': os.environ['ADMIN_AUTH_TOKEN']
        }
    )

    # assert
    assert resp.status_code == 404
