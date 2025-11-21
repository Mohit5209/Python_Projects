from src.exceptions.base_exception import BaseException


class SMTPException(BaseException):
    def __init__(self, message):
        super(SMTPException, self).__init__(message)