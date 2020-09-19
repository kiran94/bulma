import logging
from rich.logging import RichHandler
import os

FORMAT = "%(message)s"
LEVEL = os.environ.get('BULMA_LOGGING_LEVEL', 'INFO')
LOGGING_EXTRA = {
    "extra": { "markup": True }
}

logging.basicConfig(
    level=LEVEL, format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)