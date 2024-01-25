from fastapi import APIRouter, Depends, Query

from src.api.depends import get_stations_service
from src.api.routers.v1.models import AreaRequest, GetStationsByAreaResponse
from src.services.stations import StationsServices
from src.api.auth import check_api_key

router = APIRouter(prefix='/api/v1', tags=['stations'])


@router.get('/stations')
async def get_stations_by_area(
        api_key: str = Depends(check_api_key),
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
