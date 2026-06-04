import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

DEFAULT_LOG_LEVEL = logging.INFO
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_FILE = LOG_DIR / "app.log"


def ensure_log_dir() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def get_logger(name: str = __name__):
    logger = logging.getLogger(name)
    if not logger.handlers:
        fmt = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
        formatter = logging.Formatter(fmt)

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        ensure_log_dir()
        file_handler = TimedRotatingFileHandler(
            filename=str(LOG_FILE),
            when="midnight",
            backupCount=7,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        file_handler.suffix = "%Y-%m-%d"
        logger.addHandler(file_handler)

        logger.setLevel(DEFAULT_LOG_LEVEL)
        logger.propagate = False
    return logger


# convenience root logger
logger = get_logger("app")
