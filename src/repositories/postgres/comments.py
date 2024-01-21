from collections import defaultdict

import asyncpg


class CommentsRepository:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self.pool = pool

    async def get_by_station_ids(
            self,
            station_ids: list[int],
    ) -> dict[int, list[asyncpg.Record]]:
        query = """
            SELECT
                c.text,
                c.user_name,
                c.source,
                c.created_at,
                c.station_id
            FROM
                comments c
            WHERE
                c.station_id = ANY($1)
            ORDER BY
                c.created_at DESC
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
