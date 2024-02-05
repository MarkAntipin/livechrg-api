import secrets

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyHeader

from src.api.depends import get_token_service
from src.services.tokens import TokenServices

_AUTHORIZATION_HEADER_NAME = "Authorization"

AUTHORIZATION_HEADER = APIKeyHeader(name=_AUTHORIZATION_HEADER_NAME, auto_error=False)


async def check_authorization_header(
        request: Request, authorization: str = Depends(AUTHORIZATION_HEADER),
        token_service: TokenServices = Depends(get_token_service)
) -> str:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization header is missing'
        )

    if secrets.compare_digest(authorization, request.app.state.admin_auth_token):
        return authorization

    if await token_service.does_token_exist(authorization):
        return authorization
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail='Invalid authorization header'
    )
