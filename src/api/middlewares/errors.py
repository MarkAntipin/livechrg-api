import typing as tp

from fastapi import FastAPI, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware


class ErrorsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI) -> None:
        super().__init__(app)

    async def dispatch(
            self, request: Request, call_next: tp.Callable[[tp.Any], tp.Awaitable[tp.Any]]
    ) -> Response:
        try:
            return await call_next(request)
        except Exception as e:  # noqa
            # TODO: add logging here
            pass
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content='Internal Server Error',
        )