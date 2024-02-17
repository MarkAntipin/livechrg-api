import asyncpg


class ChargersMaintenanceService:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self.pool = pool

    async def identify_duplicates(self) -> str:
        query = '''
        SELECT station_id, ocpi_ids, COUNT(*)
        FROM chargers
        GROUP BY station_id, ocpi_ids
        HAVING COUNT(*) > 1;
        '''
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query)
        num_duplicates = len(rows)

        if num_duplicates == 0:
            return "No duplicate records found."
        else:
            return f"Found {num_duplicates} groups of duplicate records."

    async def delete_duplicates(self) -> None:
        query = '''
        DELETE FROM chargers
        WHERE id IN (
            SELECT c.id
            FROM chargers c
            INNER JOIN (
                SELECT station_id, ocpi_ids, MIN(id) as MinId
                FROM chargers
                GROUP BY station_id, ocpi_ids
                HAVING COUNT(*) > 1
            ) AS dg ON c.station_id = dg.station_id AND c.ocpi_ids = dg.ocpi_ids
            WHERE c.id > dg.MinId
        );
        '''
        async with self.pool.acquire() as conn:
            await conn.execute(query)
