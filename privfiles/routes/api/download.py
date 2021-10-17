from typing import Union

from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse
from starlette.authentication import requires

from ...helpers.download import stream_response
from ...responses import error_response


class DownloadAPI(HTTPEndpoint):
    @requires("authenticated")
    async def post(self, request: Request
                   ) -> Union[StreamingResponse, JSONResponse]:
        form = await request.form()
        file_id = request.path_params["file_id"]

        if "password" not in form:
            return error_response("password missing", status_code=422)

        stream = await stream_response(file_id, form["password"])

        return stream
