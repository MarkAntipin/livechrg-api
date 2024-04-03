import sys

from loguru import logger


def setup_logger() -> None:
    logger.remove()
    logger.add(sys.stdout, serialize=True)
