from fastapi import APIRouter, Depends, Query, Response, status

from src.api.depends import get_stations_service
from src.api.routers.v1.models import AddStationsRequest, AreaRequest, GetStationsByAreaResponse,\
    Source, Station
from src.services.stations import StationsServices

#TODO add new tags?
router = APIRouter(prefix='/api/v1', tags=['stations'])


@router.get('/stations-by-area')
async def get_stations_by_area(
        limit: int = Query(10),
        offset: int = Query(0),
        area: AreaRequest = Depends(),
        stations_service: StationsServices = Depends(get_stations_service)
) -> GetStationsByAreaResponse:
    stations = await stations_service.get_by_area(
        limit=limit,
        offset=offset,
        area=area,
    )
    return GetStationsByAreaResponse(
        stations=stations
    )


@router.post('/stations')
async def add_stations(
    request: AddStationsRequest,
    stations_service: StationsServices = Depends(get_stations_service)
) -> Response:
    await stations_service.add_stations(stations=request.stations)
    return Response(status_code=status.HTTP_201_CREATED)

@router.get('/stations-by-source-and-inner-id')
async def get_station_by_source_and_inner_id(
        station_source: str,
        station_inner_id: int,
        stations_service: StationsServices = Depends(get_stations_service)
) -> Station | str:
    station_id = await stations_service.stations_repo.get_station_id_by_source(
                source=station_source, inner_id=station_inner_id
            )
    if station_id:
        station = stations_service.get_by_id(station_id)
        if station:
            return station
    return 'Station not found'
