from datetime import datetime

from pydantic import BaseModel


class Coordinates(BaseModel):
    lat: float
    lon: float


class Event(BaseModel):
    charged_at: datetime
    source: str
    name: str | None = None
    is_problem: bool | None = None


class Charger(BaseModel):
    network: str
    ocpi_ids: list[str] | None = None


class Source(BaseModel):
    source: str
    inner_id: int


class AddComment(BaseModel):
    text: str
    created_at: datetime
    source: str
    user_name: str | None = None
    rating: int | None = None


class AddStation(BaseModel):
    coordinates: Coordinates
    source: Source
    chargers: list[Charger] | None = None
    events: list[Event] | None = None
    comments: list[AddComment] | None = None
    geo: dict | None = None
    rating: float | None = None
    address: str | None = None
    ocpi_ids: list[str] | None = None


class AddStationsRequest(BaseModel):
    stations: list[AddStation]


class StationSources(BaseModel):
    station_id: int
    sources: list[Source] | None = None
