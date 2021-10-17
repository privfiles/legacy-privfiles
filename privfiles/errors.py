class PrivFilesError(Exception):
    def __init__(self, msg: str = "Internal Error",
                 status_code: int = 500, *args: object) -> None:
        self.status_code = status_code
        super().__init__(msg, *args)


class KeyNotActiveError(PrivFilesError):
    def __init__(self, msg: str = "Key is not active, please email us",
                 status_code: int = 402, *args: object) -> None:
        super().__init__(msg=msg, status_code=status_code, *args)


class DataCapError(PrivFilesError):
    def __init__(self, msg: str = "You have hit your data cap",
                 status_code: int = 507, *args: object) -> None:
        super().__init__(msg=msg, status_code=status_code, *args)


class CommentLengthError(PrivFilesError):
    def __init__(self, msg: str = "Comment is too long",
                 status_code: int = 400, *args: object) -> None:
        super().__init__(msg=msg, status_code=status_code, *args)


class ContentLengthError(PrivFilesError):
    def __init__(self, msg: str = "File too large",
                 status_code: int = 413, *args: object) -> None:
        super().__init__(msg=msg, status_code=status_code, *args)


class ZeroContentLengthError(PrivFilesError):
    def __init__(self, msg: str = "Zero content legnth",
                 status_code: int = 400, *args: object) -> None:
        super().__init__(msg=msg, status_code=status_code, *args)


class PasswordError(PrivFilesError):
    def __init__(self, msg: str = "Password or link invalid",
                 status_code: int = 400, *args: object) -> None:
        super().__init__(msg=msg, status_code=status_code, *args)
