import asyncpg


class StationsRepository:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self.pool = pool

    async def get_by_area(
            self,
            min_lon: float,
            min_lat: float,
            max_lon: float,
            max_lat: float,
            limit: int,
            offset: int,
    ) -> list[asyncpg.Record]:
        query = """
            SELECT
                s.id,
                ST_AsGeoJson(coordinates)::jsonb -> 'coordinates' as coordinates,
                s.geo,
                s.address,
                s.ocpi_ids,
                s.rating,
                json_agg(json_build_object(
                    'station_inner_id', ss.station_inner_id,
                    'source', ss.source
                )) AS sources
            FROM
                stations s
            JOIN
                sources ss ON s.id = ss.station_id
            WHERE
                ST_Intersects(s.coordinates, ST_MakeEnvelope($1, $2, $3, $4, 4326)::geography('POLYGON'))
            GROUP BY
                s.id
            ORDER BY
                s.id
            LIMIT
                $5
            OFFSET
                $6;
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                query,
                min_lon,
                min_lat,
                max_lon,
                max_lat,
                limit,
                offset
            )
        return rows
