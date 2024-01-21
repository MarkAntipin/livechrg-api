from datetime import datetime

from pydantic import BaseModel


class Coordinates(BaseModel):
    lat: float
    lon: float


class AreaRequest(BaseModel):
    ne_lat: float
    ne_lon: float
    sw_lat: float
    sw_lon: float


class Event(BaseModel):
    charged_at: datetime
    source: str
    name: str | None = None


class Charger(BaseModel):
    network: str
    ocpi_ids: list[str]


class Comment(BaseModel):
    text: str
    created_at: datetime
    source: str
    user_name: str | None = None


class Source(BaseModel):
    source: str
    inner_id: int


class Station(BaseModel):
    coordinates: Coordinates
    sources: list[Source]
    chargers: list[Charger]
    events: list[Event]
    comments: list[Comment]
    last_event: Event | None = None
    avarage_rating: float | None = None
    geo: dict | None = None
    address: str | None = None
    ocpi_ids: list[str] | None = None


class GetStationsByAreaResponse(BaseModel):
    stations: list[Station]
