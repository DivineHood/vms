from fastapi import HTTPException
class FileNotSupportedError(HTTPException):
    # Constructor or Initializer
    def __init__(self, detail = "Invalid File Format"):
        self.detail = detail
        self.status_code = 406

class FileTooLargeError(HTTPException):
    # Constructor or Initializer
    def __init__(self, detail = "File too large"):
        self.detail = detail
        self.status_code = 406