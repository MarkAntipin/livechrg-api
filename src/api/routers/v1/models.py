from __future__ import annotations

from datetime import datetime
from enum import StrEnum, auto

from pydantic import BaseModel, Field, model_validator


# get stations
class Coordinates(BaseModel):
    lat: float
    lon: float


class AreaRequest(BaseModel):
    ne_lat: float = Field(ge=-90, le=90)
    ne_lon: float = Field(ge=-180, le=180)
    sw_lat: float = Field(ge=-90, le=90)
    sw_lon: float = Field(ge=-180, le=180)

    @model_validator(mode='after')
    def sw_is_lower_left_than_ne(self) -> AreaRequest:
        is_valid = bool(
            self.sw_lat <= self.ne_lat and
            self.sw_lon <= self.ne_lon
        )

        if not is_valid:
            raise ValueError("SW corner must be lower left of the NE corner when requesting an area")
        return self


class Event(BaseModel):
    charged_at: datetime
    source: str
    name: str | None = None
    is_problem: bool | None = None


class Charger(BaseModel):
    network: str
    ocpi_ids: list[str] | None = None


class Comment(BaseModel):
    text: str
    created_at: datetime
    source: str
    user_name: str | None = None


class SourceName(StrEnum):
    charge_point = auto()
    plug_share = auto()


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
    average_rating: float | None = None
    geo: dict | None = None
    address: str | None = None
    ocpi_ids: list[str] | None = None


class GetStationsByAreaResponse(BaseModel):
    stations: list[Station]


# add stations
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
