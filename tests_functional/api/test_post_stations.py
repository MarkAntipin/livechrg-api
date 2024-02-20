import json
import os
from datetime import datetime, timezone
from typing import Any, Dict

import asyncpg
import pytest
from fastapi.testclient import TestClient


@pytest.mark.asyncio
@pytest.mark.parametrize("station_data", [
    # First case
    {
        'coordinates': {'lat': 0.55, 'lon': 0.66},
        'source': {'source': 'my_source', 'inner_id': 2024},
        'chargers': [{'network': 'network', 'ocpi_ids': ['FI777', 'FI888']}],
        'events': [{'charged_at': datetime.now(timezone.utc).isoformat(), 'source': 'my_source', 'is_problem': False}],
        'comments': [{'text': 'Great station!', 'created_at': datetime.now(timezone.utc).isoformat(),
                      'source': 'my_source', 'user_name': 'Ilia', 'rating': 5}],
        'rating': 5.0,
        'address': 'Helsinki',
        'ocpi_ids': ['HEL01', 'HEL02']
    },
    # Second case
    {
        'coordinates': {'lat': 1.23, 'lon': 4.56},
        'source': {'source': 'another_source', 'inner_id': 2025},
        'chargers': [{'network': 'another_network', 'ocpi_ids': ['FI999', 'FI1010']}],
        'events': [{'charged_at': datetime.now(timezone.utc).isoformat(),
                    'source': 'another_source', 'is_problem': True}],
        'comments': [{'text': 'Needs improvement', 'created_at': datetime.now(timezone.utc).isoformat(),
                      'source': 'another_source', 'user_name': 'Alex', 'rating': 2}],
        'rating': 3.0,
        'address': 'Espoo',
        'ocpi_ids': ['ESP01', 'ESP02']
    }
])
async def test_add_stations(client: TestClient, pg: asyncpg.Pool, station_data: Dict[str, Any]) -> None:
    # arrange
    current_datetime = datetime.now(timezone.utc).isoformat()
    station_data['events'][0]['charged_at'] = current_datetime
    station_data['comments'][0]['created_at'] = current_datetime

    # act
    resp = client.post(
        '/inner/api/stations',
        json={'stations': [station_data]},
        headers={'Authorization': os.environ['ADMIN_AUTH_TOKEN']}
    )

    # assert
    assert resp.status_code == 201

    # Dynamically check Stations based on station_data
    station = await pg.fetchrow('SELECT * FROM stations ORDER BY id DESC LIMIT 1;')
    assert station['rating'] == station_data['rating']
    assert station['address'] == station_data['address']
    assert json.loads(station['ocpi_ids']) == station_data['ocpi_ids']

    # check Coordinates
    coordinates = await pg.fetchrow(
        'SELECT ST_Y(coordinates::geometry) as lat, ST_X(coordinates::geometry) as lon '
        'FROM stations ORDER BY id DESC LIMIT 1;')
    assert abs(coordinates['lat'] - station_data['coordinates']['lat']) < 0.0001
    assert abs(coordinates['lon'] - station_data['coordinates']['lon']) < 0.0001

    # Dynamically check Sources, Chargers, Events, and Comments based on station_data
    source = await pg.fetchrow('SELECT * FROM sources ORDER BY station_inner_id DESC LIMIT 1;')
    assert source['source'] == station_data['source']['source']
    assert source['station_inner_id'] == station_data['source']['inner_id']

    charger = await pg.fetchrow('SELECT * FROM chargers ORDER BY id DESC LIMIT 1;')
    assert charger['network'] == station_data['chargers'][0]['network']
    assert json.loads(charger['ocpi_ids']) == station_data['chargers'][0]['ocpi_ids']

    event = await pg.fetchrow('SELECT * FROM events ORDER BY id DESC LIMIT 1;')
    assert event['charged_at'].isoformat() == current_datetime
    assert event['source'] == station_data['events'][0]['source']
    assert event['is_problem'] == station_data['events'][0]['is_problem']

    comment = await pg.fetchrow('SELECT * FROM comments ORDER BY id DESC LIMIT 1;')
    assert comment['text'] == station_data['comments'][0]['text']
    assert comment['created_at'].isoformat() == current_datetime
    assert comment['source'] == station_data['comments'][0]['source']
    assert comment['user_name'] == station_data['comments'][0]['user_name']
    assert comment['rating'] == station_data['comments'][0]['rating']
