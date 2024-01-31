import asyncpg
import httpx
from fastapi.testclient import TestClient

from tests_functional.helpers import add_charger, add_comment, add_event, add_source, add_station



station_id = await add_station(pg=pg, latitude=1.4, longitude=1.5, rating=5)
add_source(pg=pg, station_id=station_id, station_inner_id=1, source='plug_share')
add_comment(pg=pg, station_id=station_id, text='text', source='plug_share')
add_event(pg=pg, station_id=station_id, source='plug_share', is_problem=False)
add_charger(pg=pg, station_id=station_id, network='network')

client = httpx.Client()

resp = client.get(
        '/api/v1/stations',
        params={
            'station_source': 'plug_share',
            'station_inner_id': 1,
        }
    )

print(type(resp.content))
