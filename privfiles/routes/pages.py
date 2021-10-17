from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import RedirectResponse

from ..resources import Config, Sessions
from ..helpers.captcha import validate_captcha


class HomePage(HTTPEndpoint):
    async def get(self, request: Request):
        return Config.template.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": request.query_params["error"]
                if "error" in request.query_params else None
            }
        )


class AdvertisePage(HTTPEndpoint):
    async def get(self, request: Request):
        return Config.template.TemplateResponse(
            "advertise.html",
            {
                "request": request
            }
        )


class ReportPage(HTTPEndpoint):
    async def get(self, request: Request):
        return Config.template.TemplateResponse(
            "report.html",
            {
                "request": request
            }
        )


class ZeroPage(HTTPEndpoint):
    async def get(self, request: Request):
        return Config.template.TemplateResponse(
            "zero.html",
            {
                "request": request
            }
        )


class StorageAPIPage(HTTPEndpoint):
    async def get(self, request: Request):
        if "user" in request.session and "account" in request.session["user"]:
            account = request.session["user"]["account"]
            request.session["user"].pop("account")
        else:
            account = None

        return Config.template.TemplateResponse(
            "storage-api.html",
            {
                "request": request,
                "account": account,
                "error": request.query_params["error"]
                if "error" in request.query_params else None
            }
        )


class SharePage(HTTPEndpoint):
    async def get(self, request: Request):
        if ("user" in request.session and request.path_params["file_id"] in
                request.session["user"]):
            password = request.session["user"][request.path_params["file_id"]]
            request.session["user"].pop(request.path_params["file_id"])
        else:
            password = None

        result = await Sessions.mongo.files.find_one({
            "file_id": request.path_params["file_id"]
        })

        if result:
            comment = result["comment"]
            local_dencrypt = (
                result["local_dencrypt"]
                if "local_dencrypt" in result else False
            )
            downloads = result["downloads"] if "downloads" in result else 0
        else:
            comment = None
            local_dencrypt = False
            downloads = 0

        return Config.template.TemplateResponse(
            "share.html",
            {
                "request": request,
                "password": password,
                "comment": comment,
                "local_dencrypt": local_dencrypt,
                "downloads": downloads,
                "error": request.query_params["error"]
                if "error" in request.query_params else None
            }
        )


class TestCaptcha(HTTPEndpoint):
    async def get(self, request: Request):
        return Config.template.TemplateResponse(
            "test-captcha.html",
            {
                "request": request,
                "error": request.query_params["error"]
                if "error" in request.query_params else None,
                "correct": request.query_params["correct"]
                if "correct" in request.query_params else None
            }
        )

    async def post(self, request: Request) -> RedirectResponse:
        form = await request.form()

        if "captcha" not in form:
            return RedirectResponse(
                "/test-captcha?error=fields", status_code=302
            )

        if not validate_captcha(request, form["captcha"]):
            return RedirectResponse(
                "/test-captcha?error=captcha", status_code=302
            )

        # Used for the upload page, doesn't use the validate_captcha func
        request.session["captcha_completed"] = True

        return RedirectResponse(
            "/test-captcha?correct=true", status_code=302
        )
