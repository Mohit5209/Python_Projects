from sys import stderr
from traceback import extract_tb, format_exception
from src.utils.logger import Logger

def print_traceback(exc: Exception):
    """Logs full traceback including exception message."""
    logger = Logger.get_logger()
    try:
        traceback_str = "".join(format_exception(type(exc), exc, exc.__traceback__))
        logger.error(f"\nException occurred:\n{traceback_str}")
    except Exception as logging_error:
        logger.error(f"Logging failed: {logging_error}", file=stderr)
        logger.error("Original Error:", exc, file=stderr)
