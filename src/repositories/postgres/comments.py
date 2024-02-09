from collections import defaultdict
from datetime import datetime

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
                c.station_id,
                c.rating
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

    async def add_comment(
        self,
        station_id: int,
        text: str,
        source: str,
        created_at: datetime,
        user_name: str | None = None,
        rating: int = None,
    ) -> None:
        async with self.pool.acquire() as conn:
            query = """
                INSERT INTO comments (
                    station_id,
                    text,
                    created_at,
                    user_name,
                    source,
                    rating
                )
                VALUES
                    ($1, $2, $3, $4, $5, $6)
            """
            await conn.execute(
                query,
                station_id,
                text,
                created_at,
                user_name,
                source,
                rating
            )