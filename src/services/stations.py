import asyncio
import json

import asyncpg

from src.api.routers.v1.models import AreaRequest, Charger, Comment, Coordinates, Event, Source, Station
from src.repositories.postgres.chargers import ChargersRepository
from src.repositories.postgres.comments import CommentsRepository
from src.repositories.postgres.events import EventsRepository
from src.repositories.postgres.stations import StationsRepository
from src.utils.calculate_average_rating import calculate_average_rating


class StationsServices:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self.stations_repo = StationsRepository(pool=pool)
        self.comments_repo = CommentsRepository(pool=pool)
        self.events_repo = EventsRepository(pool=pool)
        self.chargers_repo = ChargersRepository(pool=pool)

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
        async with asyncio.TaskGroup() as tg:
            get_comments_task = tg.create_task(self.comments_repo.get_by_station_ids(station_ids))
            get_events_task = tg.create_task(self.events_repo.get_by_station_ids(station_ids))
            get_chargers_task = tg.create_task(self.chargers_repo.get_by_station_ids(station_ids))

        comment_rows_by_station_id = get_comments_task.result()
        event_rows_by_station_id = get_events_task.result()
        charger_rows_by_station_id = get_chargers_task.result()

        stations = []
        for row in station_rows:
            station_id = row['id']
            chargers = charger_rows_by_station_id.get(station_id, [])
            events = event_rows_by_station_id.get(station_id, [])
            comments = comment_rows_by_station_id.get(station_id, [])

            sources = json.loads(row['sources'])
            coordinates = json.loads(row['coordinates'])

            last_event = events[0] if events else None
            average_rating = calculate_average_rating(
                [comment['rating'] for comment in comments if comment['rating']]
            )

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
                chargers=[
                    Charger(
                        network=charger['network'],
                        ocpi_ids=charger['ocpi_ids']
                    )
                    for charger in chargers
                ],
                events=[
                    Event(
                        charged_at=event['charged_at'],
                        source=event['source'],
                        name=event['name']
                    )
                    for event in events
                ],
                comments=[
                    Comment(
                        text=comment['text'],
                        created_at=comment['created_at'],
                        user_name=comment['user_name'],
                        source=comment['source']
                    )
                    for comment in comments
                ],
                geo=json.loads(row['geo']) if row['geo'] else None,
                address=row['address'],
                ocpi_ids=json.loads(row['ocpi_ids']) if row['ocpi_ids'] else None,
                last_event=Event(
                    charged_at=last_event['charged_at'],
                    source=last_event['source'],
                    name=last_event['name']
                ) if last_event else None,
                average_rating=row['rating'] or average_rating
            )

            stations.append(station)

        return stations
