import json
import os
from datetime import UTC, datetime, timedelta

import asyncpg
from fastapi.testclient import TestClient

from tests_functional.helpers import add_event, add_source, add_station


async def test_add_stations__station_does_not_exists(client: TestClient, pg: asyncpg.Pool) -> None:
    # act
    resp = client.post(
        '/api/v1/stations',
        json={
            'stations': [
                {
                    'coordinates': {
                        'lat': 1.4,
                        'lon': 1.5,
                    },
                    'source': {
                            'source': 'plug_share',
                            'inner_id': 1,
                    },
                    'comments': [
                        {
                            'source': 'plug_share',
                            'text': 'text',
                            'created_at': '2021-01-01T00:00:00',
                        }
                    ],
                }
            ]
        },
        headers={
            'Authorization': os.environ['ADMIN_AUTH_TOKEN']
        }
    )

    # assert
    assert resp.status_code == 201

    station = await pg.fetchrow(
        """
        SELECT
            ST_AsGeoJson(coordinates)::jsonb -> 'coordinates' as coordinates,
            id
        FROM stations
        """
    )
    assert station
    coordinates = json.loads(station['coordinates'])
    assert coordinates[1] == 1.4
    assert coordinates[0] == 1.5

    source = await pg.fetchrow('SELECT * FROM sources')
    assert source
    assert source['station_id'] == station['id']
    assert source['source'] == 'plug_share'

    comment = await pg.fetchrow('SELECT * FROM comments')
    assert comment
    assert comment['station_id'] == station['id']
    assert comment['source'] == 'plug_share'
    assert comment['text'] == 'text'


async def test_add_stations__station_with_source_exists(client: TestClient, pg: asyncpg.Pool) -> None:
    # arrange
    source = 'plug_share'
    station_inner_id = 1
    station_id = await add_station(pg=pg, latitude=1.4, longitude=1.5)
    await add_source(pg=pg, station_id=station_id, station_inner_id=station_inner_id, source=source)

    # act
    resp = client.post(
        '/api/v1/stations',
        json={
            'stations': [
                {
                    'coordinates': {
                        'lat': 1.4,
                        'lon': 1.5,
                    },
                    'source': {
                            'source': source,
                            'inner_id': station_inner_id,
                    },
                    'comments': [
                        {
                            'source': 'plug_share',
                            'text': 'text',
                            'created_at': '2021-01-01T00:00:00',
                        }
                    ],
                }
            ]
        },
        headers={
            'Authorization': os.environ['ADMIN_AUTH_TOKEN']
        }
    )

    # assert
    assert resp.status_code == 201

    # new station and source is not created
    stations = await pg.fetch(
        """
        SELECT
            *
        FROM
            stations
        JOIN
            sources s ON stations.id = s.station_id
        WHERE
            s.station_inner_id = $1
        """,
        station_inner_id
    )
    assert len(stations) == 1

    # comment is created
    comment = await pg.fetchrow('SELECT * FROM comments')
    assert comment
    assert comment['station_id'] == stations[0]['id']
    assert comment['source'] == 'plug_share'
    assert comment['text'] == 'text'


async def test_add_stations__station_with_close_coordinates_exists(client: TestClient, pg: asyncpg.Pool) -> None:
    # arrange
    station_id = await add_station(pg=pg, latitude=1.4, longitude=1.5)
    await add_source(pg=pg, station_id=station_id, station_inner_id=1, source='plug_share')

    # act
    resp = client.post(
        '/api/v1/stations',
        json={
            'stations': [
                {
                    'coordinates': {
                        'lat': 1.4001,
                        'lon': 1.5001,
                    },
                    'source': {
                        'source': 'charge_point',
                        'inner_id': 2,
                    }
                }
            ]
        },
        headers={
            'Authorization': os.environ['ADMIN_AUTH_TOKEN']
        }
    )

    # assert
    assert resp.status_code == 201

    # new station is not created
    stations = await pg.fetch("""SELECT * FROM stations""")
    assert len(stations) == 1

    # new source is created
    sources = await pg.fetch("""SELECT * FROM sources""")
    assert [s['source'] for s in sources] == ['plug_share', 'charge_point']


async def test_add_stations__station_with_source_exists__add_new_events(
        client: TestClient, pg: asyncpg.Pool
) -> None:
    # arrange
    station_inner_id = 1
    source = 'plug_share'

    station_id = await add_station(pg=pg, latitude=1.4, longitude=1.5)
    await add_source(pg=pg, station_id=station_id, station_inner_id=station_inner_id, source=source)

    charged_at = datetime.now(tz=UTC)
    await add_event(pg=pg, station_id=station_id, source=source, is_problem=False, charged_at=charged_at)

    # act
    resp = client.post(
        '/api/v1/stations',
        json={
            'stations': [
                {
                    'coordinates': {
                        'lat': 1.4,
                        'lon': 1.5,
                    },
                    'source': {
                        'inner_id': station_inner_id,
                        'source': source,
                    },
                    'events': [
                        {
                            'source': source,
                            'is_problem': False,
                            'charged_at': charged_at.isoformat(),
                        },
                        {
                            'source': source,
                            'is_problem': False,
                            'charged_at': (charged_at - timedelta(days=1)).isoformat(),
                        }
                    ],
                }
            ]
        },
        headers={
            'Authorization': os.environ['ADMIN_AUTH_TOKEN']
        }
    )

    # assert
    assert resp.status_code == 201

    # new event is created; old event is not recreated
    events = await pg.fetch("""SELECT * FROM events""")
    assert len(events) == 2
