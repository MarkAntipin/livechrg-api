import logging

from fastapi import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)
formatter = logging.Formatter('[%(asctime)s] - #%(levelname)s - %(message)s')

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

logger.setLevel(logging.INFO)


async def logger_middleware(request: Request, call_next: callable) -> Response:
    request_log = {
        'log_type': 'request',
        'method': request.method,
        'url': request.url.path,
        'query-params': request.query_params,
        'path_params': request.path_params,
    }
    logger.info(request_log)

    response = await call_next(request)
    response_log = {
        'log_type': 'response',
        'status': response.status_code,
    }
    logger.info(response_log)
    return response
