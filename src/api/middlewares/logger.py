from datetime import datetime
import json
import logging

from fastapi import Request
from starlette.responses import Response


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:

        log = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
        }

        if isinstance(msg := record.msg, dict):
            log |= msg
        # if record.exc_info:
        #     log_message["exception"] = self.formatException(record.exc_info)
        return json.dumps(log)


logger = logging.getLogger(__name__)
formatter = JsonFormatter()

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

logger.setLevel(logging.INFO)


async def logger_middleware(request: Request, call_next: callable) -> Response:
    request_log = {
        'log_type': 'request',
        'method': request.method,
        'url': request.url.path,
        'query-params': dict(request.query_params),
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
