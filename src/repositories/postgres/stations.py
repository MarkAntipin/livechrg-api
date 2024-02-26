import json

import asyncpg

from src.api.routers.inner.models import Source
from src.api.routers.v1.models import SourceName


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

    async def get_by_id(
            self,
            station_id: int,
    ) -> asyncpg.Record | None:
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
                s.id = $1
            GROUP BY s.id;
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                query,
                station_id
            )
        return rows[0] if rows else None

    async def get_by_source_and_inner_id(
            self,
            station_source: SourceName,
            station_inner_id: int
    ) -> asyncpg.Record | None:
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
                ss.source = $1 AND
                ss.station_inner_id = $2
            GROUP BY s.id;
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                query,
                station_source,
                station_inner_id
            )
        return rows[0] if rows else None

    async def get_station_id_by_source(self, source: str, inner_id: int) -> int | None:
        query = """
            SELECT
                station_id
            FROM
                sources
            WHERE
                source = $1 AND
                station_inner_id = $2;
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                query,
                source,
                inner_id
            )
        return row['station_id'] if row else None

    async def get_station_id_by_coordinates(self, lon: float, lat: float, distance_threshold: int = 100) -> int | None:
        query = """
            SELECT
                id
            FROM
                stations
            WHERE
                ST_DWithin(coordinates, ST_Point($1, $2)::geography, $3)
            LIMIT
                1;
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                query,
                lon,
                lat,
                distance_threshold
            )
        return row['id'] if row else None

    async def add_source(
            self,
            station_id: int,
            inner_id: int,
            source: str
    ) -> None:
        query = """
            INSERT INTO
                sources (
                    station_id,
                    station_inner_id,
                    source
                )
            VALUES ($1, $2, $3);
        """
        async with self.pool.acquire() as conn:
            await conn.execute(
                query,
                station_id,
                inner_id,
                source
            )

    async def add_station(
            self,
            lon: float,
            lat: float,
            rating: int | None = None,
            geo: dict | None = None,
            address: str | None = None,
            ocpi_ids: list[str] | None = None
    ) -> int:
        query = """
            INSERT INTO
                stations (
                    coordinates,
                    geo,
                    address,
                    ocpi_ids,
                    rating
                )
            VALUES (
                    ST_Point($1, $2),
                     $3,
                    $4,
                    $5,
                    $6
                )
            RETURNING id;
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                query,
                lon,
                lat,
                json.dumps(geo) if geo else None,
                address,
                json.dumps(ocpi_ids) if ocpi_ids else None,
                rating
            )
        return row['id']

    async def get_inner_id_and_source_by_id(self, station_id: int) -> list[Source] | None:
        query = """
            SELECT source, station_inner_id
            FROM sources
            WHERE station_id = $1
        """
        records = await self.pool.fetch(query, station_id)
        if not records:
            return None

        return [Source(source=record['source'], inner_id=record['station_inner_id']) for record in records]

