import os
import logging
from logging.handlers import RotatingFileHandler


def setup_logging(log_file: str = "logs/spimex_etl.log", level=logging.INFO):
    logger = logging.getLogger()
    logger.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    )

    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    if logger.hasHandlers():
        logger.handlers.clear()

    ch = logging.StreamHandler()
    ch.setFormatter(formatter)

    fh = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3)
    fh.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)