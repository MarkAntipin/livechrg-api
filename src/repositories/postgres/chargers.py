import json
from collections import defaultdict

import asyncpg


class ChargersRepository:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self.pool = pool

    async def get_by_station_ids(
            self,
            station_ids: list[int],
    ) -> dict[int, list[asyncpg.Record]]:
        query = """
            SELECT
                ch.ocpi_ids,
                ch.network,
                ch.station_id
            FROM
                chargers ch
            WHERE
                ch.station_id = ANY($1)
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                query,
                station_ids
            )
        res = defaultdict(list)
        for row in rows:
            res[row['station_id']].append(row)
        return res

    async def add_charger(
        self,
        station_id: int,
        ocpi_ids: dict | None = None,
        network: str | None = None
    ) -> None:
        async with self.pool.acquire() as conn:
            query = """
                INSERT INTO chargers (
                    station_id,
                    ocpi_ids,
                    network
                )
                VALUES
                    ($1, $2, $3)
            """
            await conn.execute(
                query,
                station_id,
                json.dumps(ocpi_ids) if ocpi_ids else None,
                network
            )