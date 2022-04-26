class MainException(Exception):
    def __init__(self, message=None):
        if message:
            super().__init__(message)
        else:
            super().__init__()

class CCTException(MainException):
    pass

class DataError(CCTException):
    pass