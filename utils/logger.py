import logging
import os
import sys
from logging.handlers import RotatingFileHandler

def setup_logger(name: str = "screener", level: int = logging.INFO):
    os.makedirs("logs", exist_ok=True)

    logger = logging.getLogger(name)

    # Prevent duplicate handler setup
    if logger.hasHandlers():
        return logger

    logger.setLevel(level)

    # Unified formatter
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )

    # Rotating file handler: 2MB per file, 3 backups
    file_handler = RotatingFileHandler(
        "logs/app.log", maxBytes=2_000_000, backupCount=3
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    # Console handler with UTF-8 encoding
    console_handler = logging.StreamHandler(sys.stdout)
    try:
        console_handler.stream.reconfigure(encoding='utf-8')
    except Exception:
        pass  # fallback silently if reconfigure() not supported

    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
