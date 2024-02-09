from fastapi import Request

from src.services.stations import StationsServices


async def get_stations_service(request: Request) -> StationsServices:
    return StationsServices(pool=request.app.state.pool)
