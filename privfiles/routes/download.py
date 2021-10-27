from typing import Union
from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import RedirectResponse, StreamingResponse

from ..helpers.captcha import validate_captcha
from ..helpers.download import stream_response
from ..errors import PasswordError


class DownloadDecryptFile(HTTPEndpoint):
    async def post(self, request: Request
                   ) -> Union[StreamingResponse, RedirectResponse]:
        form = await request.form()
        file_id = request.path_params["file_id"]

        if ("password" not in form or
            ("premium_key" not in request.session
                and "captcha" not in form)):
            return RedirectResponse(
                f"/share/{file_id}?error=fields",
                status_code=302
            )

        if ("premium_key" not in request.session
                and not validate_captcha(request, form["captcha"])):
            return RedirectResponse(
                f"/share/{file_id}/{form['password']}?error=captcha",
                status_code=302
            )

        try:
            stream = await stream_response(file_id, form["password"])
        except PasswordError:
            return RedirectResponse(
                f"/share/{file_id}?error=password-or-link-or-deleted",
                status_code=302
            )

        return stream
