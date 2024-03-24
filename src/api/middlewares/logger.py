from fastapi import Request
from starlette.responses import Response

from src.utils.logging.logger import logger


async def logger_middleware(request: Request, call_next: callable) -> Response:
    request_log = {
        'method': request.method,
        'url': request.url.path,
        'query-params': dict(request.query_params),
        'path_params': request.path_params,
    }
    logger.info("Request log", extra={"extra": request_log})

    try:
        response = await call_next(request)
        response_log = {
            'status': response.status_code,
        }
        logger.info("Response log", extra={"extra": response_log})
        return response
    except Exception as e:
        logger.error(e, exc_info=True)
