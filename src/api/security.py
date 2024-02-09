import secrets

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyHeader

_AUTHORIZATION_HEADER_NAME = "Authorization"

AUTHORIZATION_HEADER = APIKeyHeader(name=_AUTHORIZATION_HEADER_NAME, auto_error=False)


def get_authorization_header(
        request: Request, authorization: APIKeyHeader = Depends(AUTHORIZATION_HEADER)
) -> APIKeyHeader:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization header is missing'
        )

    if not secrets.compare_digest(authorization, request.app.state.admin_auth_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='Invalid authorization header'
        )
    return authorization