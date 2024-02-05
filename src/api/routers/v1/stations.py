from fastapi import APIRouter, Depends, Query, Response, status

from src.api.depends import check_api_key, get_stations_service
from src.api.routers.v1.models import AddStationsRequest, AreaRequest, GetStationsByAreaResponse
from src.services.stations import StationsServices

router = APIRouter(prefix='/api/v1', tags=['stations'])


@router.get('/stations')
async def get_stations_by_area(
        _: str = Depends(check_api_key),
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
