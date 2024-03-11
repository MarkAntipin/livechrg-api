import logging

from fastapi import Request

logger = logging.getLogger(__name__)
formatter = logging.Formatter('[%(asctime)s] - #%(levelname)s - %(message)s')

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

logger.setLevel(logging.INFO)


async def logger_middleware(request: Request, call_next):
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
    }
    logger.info(response_log)
    return response
