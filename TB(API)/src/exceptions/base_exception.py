from src.utils.logger import Logger


class BaseException(Exception):
    """
    This class is responsible for custom exception handling
    """
    message = ''

    def __init__(self, message):
        self.message = message
        (Logger().get_logger()).error(message)