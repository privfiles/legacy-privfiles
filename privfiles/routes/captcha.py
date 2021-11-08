from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import Response

from io import BytesIO

from ..resources import Sessions, Config


class CaptchaGen(HTTPEndpoint):
    async def get(self, request: Request) -> Response:
        captcha = Sessions.captcha.gen_captcha_image(
            difficult_level=Config.captcha.difficult_level,
            multicolor=Config.captcha.multicolor,
            margin=Config.captcha.margin,
            chars_mode=Config.captcha.chars_mode
        )

        request.session["captcha"] = captcha["characters"]
        request.session["captcha_completed"] = False

        buffer = BytesIO()
        captcha["image"].save(buffer, format="PNG")

        return Response(
            buffer.getvalue(),
            media_type="image/png"
        )
