from src.exceptions.base_exception import BaseException


class DBException(BaseException):
    def __init__(self, message):
        super(DBException, self).__init__(message)