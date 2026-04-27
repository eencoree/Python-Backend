import logging
from logging.handlers import RotatingFileHandler


def setup_logging(log_file: str = "spimex_etl_v3_tosql.log", level=logging.INFO):
    """
    Настраивает глобальное логирование для всех модулей проекта.
    """
    logger = logging.getLogger()
    logger.setLevel(level)

    formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
    )

    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    fh = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
