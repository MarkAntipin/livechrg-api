from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.security import APIKeyHeader

from src.api.depends import get_stations_service
from src.api.routers.v1.models import AddStationsRequest, AreaRequest, GetStationsByAreaResponse, SourceName, Station
from src.api.security import get_authorization_header
from src.services.stations import StationsServices

router = APIRouter(prefix='/api/v1', tags=['stations'])


@router.get('/stations-by-area')
async def get_stations_by_area(
        limit: int = Query(10, le=10),
        offset: int = Query(0),
        area: AreaRequest = Depends(),
        stations_service: StationsServices = Depends(get_stations_service),
        _: APIKeyHeader = Depends(get_authorization_header)
) -> GetStationsByAreaResponse:
    stations = await stations_service.get_by_area(
        limit=limit,
        offset=offset,
        area=area,
    )
    return GetStationsByAreaResponse(
        stations=stations
    )


@router.get('/stations')
async def get_station_by_source_and_inner_id(
        station_source: str,
        station_inner_id: int,
        stations_service: StationsServices = Depends(get_stations_service),
        _: APIKeyHeader = Depends(get_authorization_header)
) -> Station:
    station = await stations_service.get_by_source_and_inner_id(
        station_source=station_source,
        station_inner_id=station_inner_id
    )
    if not station:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return station


@router.post('/stations', status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def add_stations(
    request: AddStationsRequest,
    stations_service: StationsServices = Depends(get_stations_service),
    _: APIKeyHeader = Depends(get_authorization_header)
) -> Response:
    await stations_service.add_stations(stations=request.stations)
    return Response(status_code=status.HTTP_201_CREATED)
