from typing import Any
from starlette.responses import JSONResponse


def error_response(error: str, **kwargs) -> JSONResponse:
    if "status_code" not in kwargs:
        kwargs["status_code"] = 500
    return JSONResponse({"data": None, "error": error}, **kwargs)


def response(data: Any = None, **kwargs) -> JSONResponse:
    return JSONResponse({"data": data, "error": False}, **kwargs)
