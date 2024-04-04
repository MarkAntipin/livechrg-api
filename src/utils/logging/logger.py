import logging

from src.utils.logging.formatter import JsonFormatter

logger = logging.getLogger(__name__)
formatter = JsonFormatter()

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

logger.setLevel(logging.INFO)
