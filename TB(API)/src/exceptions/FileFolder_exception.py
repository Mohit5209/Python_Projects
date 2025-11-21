from src.exceptions.base_exception import BaseException


class FileNotFoundException(BaseException):
    def __init__(self, message):
        super(FileNotFoundException, self).__init__(message)


class FolderNotFoundException(BaseException):
    def __init__(self, message):
        super(FolderNotFoundException, self).__init__(message)


class EmptyFolderException(BaseException):
    def __init__(self, message):
        super(EmptyFolderException, self).__init__(message)


class BoolValException(BaseException):
    def __init__(self, message):
        super().__init__(message)