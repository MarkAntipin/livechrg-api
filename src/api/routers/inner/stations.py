from fastapi import APIRouter, Depends, Response, status
from fastapi.security import APIKeyHeader

from src.api.depends import get_stations_service
from src.api.routers.inner.models import AddStationsRequest, StationSources
from src.api.security import check_authorization_header
from src.services.stations import StationsServices

router = APIRouter(prefix='/inner/api', tags=['stations'])


@router.post('/stations', status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def add_stations(
        request: AddStationsRequest,
        stations_service: StationsServices = Depends(get_stations_service),
        _: APIKeyHeader = Depends(check_authorization_header)
) -> Response:
    await stations_service.add_stations(stations=request.stations)
    return Response(status_code=status.HTTP_201_CREATED)


@router.get('/sources', include_in_schema=False)
async def get_station_inner_id_and_source_by_station_id(
        station_ids: str,
        stations_service: StationsServices = Depends(get_stations_service),
        _: APIKeyHeader = Depends(check_authorization_header)
) -> list[StationSources]:
    station_ids = [int(id_str) for id_str in station_ids.split(',')]
    station_sources = await stations_service.get_station_inner_id_and_source_by_station_id(
        station_ids=station_ids)
    return station_sources
