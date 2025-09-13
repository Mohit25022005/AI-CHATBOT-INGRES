# app/utils/logger.py
import logging
import sys

def get_logger(name=__name__):
    logger = logging.getLogger(name)
    if not logger.handlers:
        h = logging.StreamHandler(sys.stdout)
        fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
        h.setFormatter(fmt)
        logger.addHandler(h)
        logger.setLevel(logging.INFO)
    return logger

logger = get_logger("ai-chatbot-ingres")
