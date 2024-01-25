from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

API_KEYS = [
    "9d207bf0-10f5-4d8f-a479-22ff5aeff8d1",
    "123"
]

API_KEY_HEADER = APIKeyHeader(name="api-key")


def check_api_key(api_key_header: str = Security(API_KEY_HEADER)) -> str:
    if api_key_header in API_KEYS:
        return api_key_header
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="API KEY is invalid or missing")
