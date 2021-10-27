from starlette.endpoints import HTTPEndpoint
from starlette.responses import RedirectResponse
from starlette.requests import Request

from secrets import token_urlsafe

from ..resources import Config, Sessions
from ..helpers.captcha import validate_captcha


class PremiumPage(HTTPEndpoint):
    async def get(self, request: Request):
        if "user" in request.session and "premium" in request.session["user"]:
            premium_key = request.session["user"]["premium"]
            request.session["user"].pop("premium")
        else:
            premium_key = None

        return Config.template.TemplateResponse(
            "premium.html",
            {
                "request": request,
                "premium_key": premium_key,
                "error": request.query_params["error"]
                if "error" in request.query_params else None
            }
        )

    async def post(self, request: Request) -> RedirectResponse:
        form = await request.form()

        if ("captcha" not in form or not
                validate_captcha(request, form["captcha"])):
            return RedirectResponse(
                "/premium?error=captcha",
                status_code=302
            )

        key = token_urlsafe(64)

        await Sessions.mongo.premium.insert_one({
            "key": key,
            "active": False,
            "uploads": 0,
            "max_uploads": 0
        })

        if "user" in request.session:
            request.session["user"]["premium"] = key
        else:
            request.session["user"] = {"premium": key}

        return RedirectResponse("/premium", status_code=302)
