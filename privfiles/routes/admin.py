from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import RedirectResponse

from datetime import datetime

from ..resources import Config, Sessions
from ..errors import PasswordError, FileIdError
from ..helpers.delete import delete_upload


class AdminPage(HTTPEndpoint):
    async def get(self, request: Request):
        return Config.template.TemplateResponse(
            "admin.html",
            {
                "request": request,
                "error": request.query_params["error"]
                if "error" in request.query_params else None
            }
        )


class AdminDeleteUpload(HTTPEndpoint):
    async def post(self, request: Request) -> RedirectResponse:
        form = await request.form()

        if "password" not in form or "file-id" not in form:
            return RedirectResponse("/admin?error=fields", status_code=302)

        try:
            await delete_upload(form["password"], form["file-id"])
        except PasswordError:
            return RedirectResponse(
                "/admin?error=password-or-link-or-deleted", status_code=302
            )
        except FileIdError:
            return RedirectResponse("/admin?error=file-id", status_code=302)
        else:
            return RedirectResponse("/admin", status_code=302)


class AdminUpdateAccount(HTTPEndpoint):
    async def post(self, request: Request) -> RedirectResponse:
        form = await request.form()

        if "username" not in form:
            return RedirectResponse("/admin?error=fields", status_code=302)

        if await Sessions.mongo.api.count_documents(
                {"username": form["username"]}) == 0:
            return RedirectResponse(
                "/admin?error=invalid-user", status_code=302
            )

        values = {
            "active": True
        }
        if "datacap" in form and form["datacap"]:
            values["data_cap"] = (  # type: ignore
                float(form["datacap"]) * 1074000000
            )

        if "maxupload" in form and form["maxupload"]:
            values["max_upload"] = (  # type: ignore
                float(form["maxupload"]) * 1049000
            )

        if "expires" in form and form["expires"]:
            values["next_payment"] = datetime.strptime(  # type: ignore
                form["expires"], "%Y-%m-%d"
            )

        await Sessions.mongo.api.update_one(
            {"username": form["username"]},
            {"$set": values}
        )

        return RedirectResponse("/admin", status_code=302)
