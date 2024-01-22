import json
from datetime import UTC, datetime

import asyncpg


async def add_station(
    pg: asyncpg.Pool,
    latitude: float,
    longitude: float,
    geo: dict = None,
    address: str = 'address',
    ocpi_ids: dict = None,
    rating: float = 10,
) -> int:
    row = await pg.fetchrow(
        """
        INSERT INTO stations (
            coordinates,
            geo,
            address,
            ocpi_ids,
            rating
        )
        VALUES
            (ST_Point($1, $2), $3, $4, $5, $6)
        ON CONFLICT (id) DO NOTHING
        RETURNING id
        """,
        longitude,
        latitude,
        json.dumps(geo) if geo else None,
        address,
        json.dumps(ocpi_ids) if ocpi_ids else None,
        rating
    )
    return row['id']


async def add_source(
    pg: asyncpg.Pool,
    station_id: int,
    station_inner_id: int,
    source: str
) -> None:
    await pg.execute(
        """
        INSERT INTO sources (
            station_id,
            station_inner_id,
            source
        )
        VALUES
            ($1, $2, $3)
        """,
        station_id,
        station_inner_id,
        source
    )


async def add_comment(
    pg: asyncpg.Pool,
    station_id: int,
    text: str,
    source: str,
    user_name: str | None = None,
    rating: int = None,
) -> None:
    await pg.execute(
        """
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
        """,
        station_id,
        text,
        datetime.now(UTC),
        user_name,
        source,
        rating
    )


async def add_event(
    pg: asyncpg.Pool,
    station_id: int,
    source: str,
    is_problem: bool,
    name: str | None = None
) -> None:
    await pg.execute(
        """
        INSERT INTO events (
            station_id,
            source,
            charged_at,
            name,
            is_problem
        )
        VALUES
            ($1, $2, $3, $4, $5)
        """,
        station_id,
        source,
        datetime.now(UTC),
        name,
        is_problem
    )


async def add_charger(
    pg: asyncpg.Pool,
    station_id: int,
    ocpi_ids: dict | None = None,
    network: str | None = None
) -> None:
    await pg.execute(
        """
        INSERT INTO chargers (
            station_id,
            ocpi_ids,
            network
        )
        VALUES
            ($1, $2, $3)
        """,
        station_id,
        json.dumps(ocpi_ids) if ocpi_ids else None,
        network
    )
