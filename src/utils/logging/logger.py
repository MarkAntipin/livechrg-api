import sys

from loguru import logger

logger.remove()
logger.add(sys.stdout, serialize=True)
logger.info("That's it, beautiful and simple logging!")
