from collections import defaultdict

import asyncpg


class EventsRepository:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self.pool = pool

    async def get_by_station_ids(
            self,
            station_ids: list[int],
    ) -> dict[int, list[asyncpg.Record]]:
        query = """
            SELECT
                e.name,
                e.source,
                e.charged_at,
                e.station_id
            FROM
                events e
            WHERE
                e.station_id = ANY($1)
            ORDER BY
                e.charged_at DESC
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
