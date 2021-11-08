from typing import Any, AsyncGenerator, Callable, Union
from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse, StreamingResponse
from starlette.datastructures import UploadFile

from ..helpers.upload import upload_file
from ..errors import (
    CommentLengthError, ContentLengthError, ZeroContentLengthError
)
from ..resources import Sessions, Config


async def show_progress(upload: AsyncGenerator) -> AsyncGenerator[str, None]:
    yield '''<html>
    <head>
        <title>privfiles upload</title>
        <link rel="stylesheet" href="/static/bootstrap/css/bootstrap.min.css">
        <link rel="stylesheet" href="/static/css/styles.min.css">
    </head>
    <body>
    <h2>Uploading progress</h2>
    <ul>'''

    try:
        yield '<li>0.000 MBs</li>'

        user_key = b""
        file_id = ""
        async for _, file_id, user_key, content_length in upload:
            yield f'<li>{round(content_length / 1049000, 3)} MBs</li>'
    except CommentLengthError:
        yield '</ul></body></html>'
        yield '<meta http-equiv="refresh" content="0; URL=/?error=comment"/>'
    except ContentLengthError:
        yield '</ul></body></html>'
        yield '<meta http-equiv="refresh" content="0; URL=/?error=size"/>'
    except ZeroContentLengthError:
        yield '</ul></body></html>'
        yield '<meta http-equiv="refresh" content="0; URL=/?error=file-content"/>'
    else:
        yield '</ul></body></html>'
        yield f'<meta http-equiv="refresh" content="0; URL=/share/{file_id}?user_key={user_key.decode()}"/>'


class UploadEncryptFile(HTTPEndpoint):
    async def post(self, request: Request
                   ) -> Union[JSONResponse, RedirectResponse, StreamingResponse]:
        form = await request.form()

        if "upload" not in form or not isinstance(form["upload"], UploadFile):
            return RedirectResponse("/?error=fields", status_code=302)

        if "premium_key" not in request.session:
            if ("captcha_completed" not in request.session
                    or not request.session["captcha_completed"]):
                return RedirectResponse("/?error=captcha", status_code=302)

            request.session["captcha_completed"] = False

            max_size = Config.size.max_size
        else:
            result = await Sessions.mongo.premium.find_one({
                "key": request.session["premium_key"]
            })

            # If next upload will be above max uploads
            if result["uploads"] > result["max_uploads"]:
                request.session["premium_max"] = True
                request.session.pop("premium_key")

            await Sessions.mongo.premium.update_one(
                {"key": request.session["premium_key"]},
                {
                    "$inc": {"uploads": 1}
                },
                upsert=True
            )

            max_size = Config.size.premium_size

        return StreamingResponse(
            show_progress(
                upload_file(form, max_upload=max_size)
            ),
            media_type="text/html"
        )
