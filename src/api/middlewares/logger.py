from fastapi import Request
from loguru import logger
from starlette.responses import Response


@logger.catch
async def logger_middleware(request: Request, call_next: callable) -> Response:
    request_log = {
        'method': request.method,
        'url': request.url.path,
        'query-params': dict(request.query_params),
        'path_params': request.path_params,
    }
    logger.info(request_log)

    response = await call_next(request)
    response_log = {
        'status': response.status_code,
    }
    logger.info(response_log)
    return response
