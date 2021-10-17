from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import Response

import string
import random

from ..resources import Sessions


class CaptchaGen(HTTPEndpoint):
    async def get(self, request: Request) -> Response:
        text = ''.join(random.choices(
            string.ascii_lowercase
            + string.digits
            + "@&%$#",
            k=6
        ))

        request.session["captcha"] = text
        request.session["captcha_completed"] = False

        return Response(
            Sessions.captcha.generate(text).getvalue(),
            media_type="image/png"
        )
