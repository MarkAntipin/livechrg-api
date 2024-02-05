import asyncio
import json

import asyncpg

from typing import List
from src.api.routers.v1.models import AddStation, AreaRequest, Charger, Comment, Coordinates, Event, Source, Station
from src.repositories.postgres.chargers import ChargersRepository
from src.repositories.postgres.comments import CommentsRepository
from src.repositories.postgres.events import EventsRepository
from src.repositories.postgres.stations import StationsRepository
from src.utils.calculate_average_rating import calculate_average_rating
from src.utils.filter_entities import filter_chargers, filter_comments, filter_events


class StationsServices:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self.stations_repo = StationsRepository(pool=pool)
        self.comments_repo = CommentsRepository(pool=pool)
        self.events_repo = EventsRepository(pool=pool)
        self.chargers_repo = ChargersRepository(pool=pool)

    async def _get_station_extra_data(
            self, station_ids: list[int]
    ) -> tuple[dict[int, list[asyncpg.Record]], dict[int, list[asyncpg.Record]], dict[int, list[asyncpg.Record]]]:

        async with asyncio.TaskGroup() as tg:
            get_comments_task = tg.create_task(self.comments_repo.get_by_station_ids(station_ids))
            get_events_task = tg.create_task(self.events_repo.get_by_station_ids(station_ids))
            get_chargers_task = tg.create_task(self.chargers_repo.get_by_station_ids(station_ids))

        comment_rows_by_station_id = get_comments_task.result()
        event_rows_by_station_id = get_events_task.result()
        charger_rows_by_station_id = get_chargers_task.result()

        return comment_rows_by_station_id, event_rows_by_station_id, charger_rows_by_station_id

    @staticmethod
    def _format_comments(comment_rows: list[asyncpg.Record]) -> list[Comment]:
        return [
            Comment(
                text=comment['text'],
                created_at=comment['created_at'],
                user_name=comment['user_name'],
                source=comment['source']
            )
            for comment in comment_rows
        ]

    @staticmethod
    def _format_events(event_rows: list[asyncpg.Record]) -> list[Event]:
        return [
            Event(
                charged_at=event['charged_at'],
                source=event['source'],
                name=event['name'],
                is_problem=event['is_problem']
            )
            for event in event_rows
        ]

    @staticmethod
    def _format_chargers(charger_rows: List[dict]) -> List[Charger]:
        """
        Process a list of charger data and return a list of unique Charger objects.

        This function parses charger data, where each charger includes a network and possibly multiple OCPI IDs.
        It ensures that each charger, uniquely identified by a combination of network and individual OCPI ID,
        is represented by a single Charger object.
        Chargers with multiple OCPI IDs are treated as separate chargers under the same network.

        Args:
            charger_rows (List[dict]): A list of dictionaries, each representing charger data with 'network' and 'ocpi_ids' keys.
            'network' is a string indicating the charger's network, and
            'ocpi_ids' is a JSON string representing one or more OCPI IDs.

        Returns:
            List[Charger]: A list of unique Charger objects.
            Chargers with multiple OCPI IDs are split into multiple Charger objects, each with a single OCPI ID.
            If 'ocpi_ids' is empty or not provided, it is set to None in the resulting Charger object.

        Unique chargers are determined by their network and individual OCPI IDs.
        Duplicate chargers (same network and OCPI ID) are not included in the returned list.
        """
        unique_chargers = set()
        formatted_chargers = []
        for charger in charger_rows:
            network = charger['network']
            ocpi_ids = json.loads(charger.get('ocpi_ids', 'null')) if charger.get('ocpi_ids') else None

            if ocpi_ids and isinstance(ocpi_ids, list):
                # Split chargers with multiple ocpi_ids into separate chargers
                for ocpi_id in ocpi_ids:
                    charger_tuple = (network, ocpi_id)
                    if charger_tuple not in unique_chargers:
                        unique_chargers.add(charger_tuple)
                        formatted_chargers.append(Charger(network=network, ocpi_ids=[ocpi_id]))
            else:
                # Handle single ocpi_id, None, or empty list
                charger_tuple = (network, tuple(ocpi_ids) if isinstance(ocpi_ids, list) else ocpi_ids)
                if charger_tuple not in unique_chargers:
                    unique_chargers.add(charger_tuple)
                    formatted_chargers.append(Charger(network=network, ocpi_ids=ocpi_ids if ocpi_ids else None))

        return formatted_chargers

    async def get_by_area(
            self,
            limit: int,
            offset: int,
            area: AreaRequest,
    ) -> list[Station]:
        station_rows = await self.stations_repo.get_by_area(
            min_lat=area.sw_lat,
            min_lon=area.sw_lon,
            max_lat=area.ne_lat,
            max_lon=area.ne_lon,
            limit=limit,
            offset=offset,
        )
        station_ids = [row['id'] for row in station_rows]

        (
            comment_rows_by_station_id,
            event_rows_by_station_id,
            charger_rows_by_station_id
        ) = await self._get_station_extra_data(station_ids=station_ids)

        stations = []
        for row in station_rows:
            station_id = row['id']
            charger_rows = charger_rows_by_station_id.get(station_id, [])
            events_rows = event_rows_by_station_id.get(station_id, [])
            comments_rows = comment_rows_by_station_id.get(station_id, [])

            sources = json.loads(row['sources'])
            coordinates = json.loads(row['coordinates'])

            average_rating = calculate_average_rating(
                [comments_row['rating'] for comments_row in comments_rows if comments_row['rating']]
            )

            events = self._format_events(event_rows=events_rows)
            last_event = events[0] if events else None

            station = Station(
                coordinates=Coordinates(
                    lat=coordinates[1],
                    lon=coordinates[0]
                ),
                sources=[
                    Source(
                        source=source['source'],
                        inner_id=source['station_inner_id']
                    ) for source in sources
                ],
                chargers=self._format_chargers(charger_rows=charger_rows),
                events=events,
                comments=self._format_comments(comment_rows=comments_rows),
                geo=json.loads(row['geo']) if row['geo'] else None,
                address=row['address'],
                ocpi_ids=json.loads(row['ocpi_ids']) if row['ocpi_ids'] else None,
                last_event=last_event if last_event else None,
                average_rating=row['rating'] or average_rating
            )

            stations.append(station)

        return stations

    async def get_by_source_and_inner_id(
            self,
            station_source: str,
            station_inner_id: int
    ) -> Station | None:
        station_id = await self.stations_repo.get_station_id_by_source(
            source=station_source, inner_id=station_inner_id
        )

        if not station_id:
            return

        row = await self.stations_repo.get_by_id(station_id=station_id)

        if not row:
            return

        (
            comments_rows_by_station_id,
            events_rows_by_station_id,
            charger_rows_by_station_id
        ) = await self._get_station_extra_data(station_ids=[station_id])

        charger_rows = charger_rows_by_station_id.get(station_id, [])
        events_rows = events_rows_by_station_id.get(station_id, [])
        comments_rows = comments_rows_by_station_id.get(station_id, [])

        sources = json.loads(row['sources'])
        coordinates = json.loads(row['coordinates'])

        average_rating = calculate_average_rating(
            [comments_row['rating'] for comments_row in comments_rows if comments_row['rating']]
        )

        events = self._format_events(event_rows=events_rows)
        last_event = events[0] if events else None

        station = Station(
            coordinates=Coordinates(
                lat=coordinates[1],
                lon=coordinates[0]
            ),
            sources=[
                Source(
                    source=source['source'],
                    inner_id=source['station_inner_id']
                ) for source in sources
            ],
            chargers=self._format_chargers(charger_rows=charger_rows),
            events=events,
            comments=self._format_comments(comment_rows=comments_rows),
            geo=json.loads(row['geo']) if row['geo'] else None,
            address=row['address'],
            ocpi_ids=json.loads(row['ocpi_ids']) if row['ocpi_ids'] else None,
            last_event=last_event if last_event else None,
            average_rating=row['rating'] or average_rating
        )
        return station

    async def add_stations(self, stations: list[AddStation]) -> None:
        for station in stations:
            # try to find station by source
            station_id = await self.stations_repo.get_station_id_by_source(
                source=station.source.source, inner_id=station.source.inner_id
            )
            if not station_id:
                # try to find station by coordinates
                station_id = await self.stations_repo.get_station_id_by_coordinates(
                    lat=station.coordinates.lat, lon=station.coordinates.lon
                )
                if station_id:
                    # station exists, add source
                    await self.stations_repo.add_source(
                        station_id=station_id,
                        source=station.source.source,
                        inner_id=station.source.inner_id
                    )
                else:
                    # add new station with source
                    station_id = await self.stations_repo.add_station(
                        lat=station.coordinates.lat,
                        lon=station.coordinates.lon,
                        geo=station.geo,
                        address=station.address,
                        ocpi_ids=station.ocpi_ids,
                        rating=station.rating
                    )
                    await self.stations_repo.add_source(
                        station_id=station_id,
                        source=station.source.source,
                        inner_id=station.source.inner_id
                    )

            # get already saved data
            (
                comment_rows_by_station_id,
                event_rows_by_station_id,
                charger_rows_by_station_id
            ) = await self._get_station_extra_data(station_ids=[station_id])

            presented_events = self._format_events(event_rows=event_rows_by_station_id.get(station_id, []))
            presented_comments = self._format_comments(comment_rows=comment_rows_by_station_id.get(station_id, []))
            presented_chargers = self._format_chargers(charger_rows=charger_rows_by_station_id.get(station_id, []))

            # filter new data
            events_to_add = filter_events(old_events=presented_events, new_events=station.events or [])
            comments_to_add = filter_comments(old_comments=presented_comments, new_comments=station.comments or [])
            chargers_to_add = filter_chargers(old_chargers=presented_chargers, new_chargers=station.chargers or [])

            # add new data
            async with asyncio.TaskGroup() as tg:
                for event in events_to_add:
                    tg.create_task(self.events_repo.add_event(
                        station_id=station_id,
                        source=event.source,
                        charged_at=event.charged_at,
                        name=event.name,
                        is_problem=event.is_problem
                        )
                    )

                for comment in comments_to_add:
                    tg.create_task(self.comments_repo.add_comment(
                        station_id=station_id,
                        text=comment.text,
                        created_at=comment.created_at,
                        user_name=comment.user_name,
                        source=comment.source,
                        rating=comment.rating
                        )
                    )

                for charger in chargers_to_add:
                    tg.create_task(self.chargers_repo.add_charger(
                        station_id=station_id,
                        network=charger.network,
                        ocpi_ids=charger.ocpi_ids
                        )
                    )


