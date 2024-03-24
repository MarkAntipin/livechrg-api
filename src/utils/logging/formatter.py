import json
import logging
from datetime import datetime


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
