from typing import Union
from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse
from starlette.datastructures import UploadFile

from ..helpers.upload import upload_file
from ..errors import (
    CommentLengthError, ContentLengthError, ZeroContentLengthError
)
from ..responses import error_response, response


class UploadEncryptFile(HTTPEndpoint):
    async def post(self, request: Request
                   ) -> Union[JSONResponse, RedirectResponse]:
        form = await request.form()

        expects_json = (
            form["expect_json"] == "true"
            if "expect_json" in form else False
        )

        if "upload" not in form or not isinstance(form["upload"], UploadFile):
            return (
                error_response("fields") if expects_json else
                RedirectResponse("/?error=fields", status_code=302)
            )

        if ("captcha_completed" not in request.session
                or not request.session["captcha_completed"]):
            return (
                error_response("captcha") if expects_json else
                RedirectResponse("/?error=captcha", status_code=302)
            )

        request.session["captcha_completed"] = False

        try:
            file_id, user_key, _ = await upload_file(
                form, local_dencrypt=expects_json
            )
        except CommentLengthError:
            return (
                error_response("comment") if expects_json else
                RedirectResponse("/?error=comment", status_code=302)
            )
        except ContentLengthError:
            return (
                error_response("size") if expects_json else
                RedirectResponse("/?error=size", status_code=302)
            )
        except ZeroContentLengthError:
            return (
                error_response("file-content") if expects_json else
                RedirectResponse("/?error=file-content", status_code=302)
            )

        if not expects_json:
            if "user" not in request.session:
                request.session["user"] = {
                    file_id: user_key.decode()
                }
            else:
                request.session["user"][file_id] = user_key.decode()

            return RedirectResponse(
                "/share/" + file_id,
                status_code=302,
            )
        else:
            return response({
                "password": user_key.decode(),
                "file_id": file_id
            })
