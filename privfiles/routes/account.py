import bcrypt

from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import RedirectResponse

from secrets import token_urlsafe

from ..helpers.captcha import validate_captcha
from ..resources import Config, Sessions


class AccountGenerate(HTTPEndpoint):
    async def post(self, request: Request) -> RedirectResponse:
        form = await request.form()

        if ("captcha" not in form or not
                validate_captcha(request, form["captcha"])):
            return RedirectResponse(
                "/storage-api?error=captcha",
                status_code=302
            )

        username = token_urlsafe()
        password = token_urlsafe(64)

        await Sessions.mongo.api.insert_one({
            "active": False,
            "data_cap": 0.0,
            "used_data": 0.0,
            "max_upload": 0.0,
            "username": username,
            "password": bcrypt.hashpw(password.encode(), bcrypt.gensalt()),
            "next_payment": None,
            "file_ids": []
        })

        if "user" in request.session:
            request.session["user"]["account"] = {
                "username": username,
                "password": password
            }
        else:
            request.session["user"] = {
                "account": {
                    "username": username,
                    "password": password
                }
            }

        return RedirectResponse("/storage-api", status_code=302)


class AccountPage(HTTPEndpoint):
    async def get(self, request: Request):
        return Config.template.TemplateResponse(
            "account-login.html",
            {
                "request": request,
                "error": request.query_params["error"]
                if "error" in request.query_params else None
            }
        )

    async def post(self, request: Request):
        form = await request.form()
        if "username" not in form or "password" not in form:
            return RedirectResponse("/account?error=fields", status_code=302)

        result = await Sessions.mongo.api.find_one({
            "username": form["username"]
        })
        if not result:
            return RedirectResponse("/account?error=login", status_code=302)

        if not bcrypt.checkpw(form["password"].encode(), result["password"]):
            return RedirectResponse("/account?error=login", status_code=302)

        return Config.template.TemplateResponse(
            "account.html",
            {
                "request": request,
                "account": result
            }
        )
