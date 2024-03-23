import json
import logging
from datetime import datetime

from fastapi import Request
from starlette.responses import Response


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:

        log = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "log_level": record.levelname,
        }

        if isinstance(msg := record.msg, dict):
            log |= msg
        if record.exc_info:
            log["exception"] = record.exc_info[0].__name__
            log["exception_message"] = str(record.exc_info[1])
            log["traceback"] = self.formatException(record.exc_info)
        return json.dumps(log)


logger = logging.getLogger(__name__)
formatter = JsonFormatter()

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

logger.setLevel(logging.INFO)


async def logger_middleware(request: Request, call_next: callable) -> Response:
    try:
        request_log = {
            'log_type': 'request',
            'method': request.method,
            'url': request.url.path,
            'query-params': dict(request.query_params),
            'path_params': request.path_params,
        }
        logger.info(request_log)
    except Exception:
        logger.error("Error", exc_info=True)

    try:
        response = await call_next(request)
        response_log = {
            'log_type': 'response',
            'status': response.status_code,
        }
        logger.info(response_log)
        return response
    except Exception:
        logger.error("Error", exc_info=True)
