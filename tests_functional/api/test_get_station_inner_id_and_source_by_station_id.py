import os

import asyncpg
from starlette.testclient import TestClient

from tests_functional.helpers import add_source, add_station


async def test_get_station_inner_id_and_source_by_station_id(
    client: TestClient, pg: asyncpg.Pool
) -> None:
    # arrange
    station_id = await add_station(pg=pg, latitude=1.4, longitude=1.5, rating=5)
    await add_source(
        pg=pg, station_id=station_id, station_inner_id=1, source="plug_share"
    )

    # act
    resp = client.get(
        "/inner/api/sources",
        params={
            "station_ids": station_id,
        },
        headers={"Authorization": os.environ["ADMIN_AUTH_TOKEN"]},
    )

    station_sources = resp.json()

    assert (
        resp.status_code == 200
    ), f"Unexpected error: {station_sources.get('detail', 'No detail provided')}"
    assert len(station_sources) == 1
    assert station_sources[0]["station_id"] == station_id
    assert "sources" in station_sources[0]
    assert len(station_sources[0]["sources"]) == 1
    assert station_sources[0]["sources"][0]["source"] == "plug_share"
    assert station_sources[0]["sources"][0]["inner_id"] == 1
