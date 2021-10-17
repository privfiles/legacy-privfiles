from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.exceptions import HTTPException

from ..responses import error_response
from ..errors import PrivFilesError


def on_auth_error(request: Request, exc: Exception) -> JSONResponse:
    return error_response(str(exc), status_code=401)


def on_privfile_error(request: Request, exc: PrivFilesError) -> JSONResponse:
    return error_response(str(exc), status_code=exc.status_code)


def on_http_error(request: Request, exc: HTTPException) -> JSONResponse:
    return error_response(exc.detail, status_code=exc.status_code)
