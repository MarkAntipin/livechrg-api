from fastapi import Request, HTTPException, Security, status, Depends
from fastapi.security import APIKeyHeader

from src.services.stations import StationsServices
from src.services.tokens import TokenServices

API_KEY_HEADER = APIKeyHeader(name="api-key")


async def get_stations_service(request: Request) -> StationsServices:
    return StationsServices(pool=request.app.state.pool)


async def get_token_service(request: Request) -> TokenServices:
    return TokenServices(pool=request.app.state.pool)


async def check_api_key(
        api_key_header: str = Security(API_KEY_HEADER),
        token_service: TokenServices = Depends(get_token_service)
) -> str:
    # TODO: 401 if no token passed
    if await token_service.does_token_exist(api_key_header):
        return api_key_header
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="API KEY is invalid or missing")
