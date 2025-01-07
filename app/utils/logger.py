# app/utils/logger.py

import logging

def get_logger(name: str = __name__) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(levelname)s:%(name)s:%(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
