import logging

from fastapi import Request

logger = logging.getLogger(__name__)
formatter = logging.Formatter('[%(asctime)s] - #%(levelname)s - %(message)s')

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
file_handler = logging.FileHandler('logs.log')
console_handler.setFormatter(formatter)
logger.handlers = [console_handler, file_handler]

logger.setLevel(logging.INFO)


async def logger_middleware(request: Request, call_next):
    log_dict = {
        'method': request.method,
        'url': request.url.path
    }
    logger.info(log_dict)
    response = await call_next(request)
    return response
