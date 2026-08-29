import logging
from typing import Optional


def configure_logging(level: int = logging.INFO, logger_name: str = "ai_risk_manager") -> logging.Logger:
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    logger.propagate = False

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        logger.addHandler(handler)

    return logger
