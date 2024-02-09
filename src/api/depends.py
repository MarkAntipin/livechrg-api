from fastapi import Request

from src.services.stations import StationsServices
from src.services.tokens import TokenServices


async def get_stations_service(request: Request) -> StationsServices:
    return StationsServices(pool=request.app.state.pool)


async def get_token_service(request: Request) -> TokenServices:
    return TokenServices(pool=request.app.state.pool)
