from src.exceptions.base_exception import BaseException


class ValidationException(BaseException):
    def __init__(self, message):
        super(ValidationException, self).__init__(message)


class InvalidBucketException(BaseException):
    def __init__(self, message):
        super(InvalidBucketException, self).__init__(message)


class InvalidPathException(BaseException):
    def __init__(self, message):
        super(InvalidPathException, self).__init__(message)


class ConnectionException(BaseException):
    def __init__(self, message):
        super(ConnectionException, self).__init__(message)