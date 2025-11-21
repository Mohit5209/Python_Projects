from src.exceptions.base_exception import BaseException

class DecryptException(BaseException):
    def __init__(self, message):
        super(DecryptException, self).__init__(message)