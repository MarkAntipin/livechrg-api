from fastapi import APIRouter, Depends, Response, status
from fastapi.security import APIKeyHeader

from src.api.depends import get_stations_service
from src.api.routers.inner.models import AddStationsRequest
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
