import base64
import binascii
import bcrypt

from starlette.requests import Request
from starlette.authentication import (
    AuthenticationBackend, AuthenticationError,
    SimpleUser, AuthCredentials
)

from .resources import Sessions, Config

AUTH_ERROR = "Invalid basic auth credentials"


class BasicAuthBackend(AuthenticationBackend):
    async def authenticate(self, request: Request):
        if "Authorization" not in request.headers:
            if "key" in request.query_params:
                result = await Sessions.mongo.premium.find_one({
                    "key": request.query_params["key"],
                    "active": True
                })
                if not result:
                    return

                request.session["premium_max"] = (
                    result["uploads"] >= result["max_uploads"]
                )
                request.session["premium_key"] = result["key"]

            return

        auth = request.headers["Authorization"]
        try:
            scheme, credentials = auth.split()
            if scheme.lower() != "basic":
                return
            decoded = base64.b64decode(credentials).decode("ascii")
        except (ValueError, UnicodeDecodeError, binascii.Error):
            raise AuthenticationError(AUTH_ERROR)

        username, _, password = decoded.partition(":")

        result = await Sessions.mongo.api.find_one({
            "username": username
        })
        if not result:
            return

        if not bcrypt.checkpw(password.encode(), result["password"]):
            raise AuthenticationError(AUTH_ERROR)

        if not result["active"]:
            raise AuthenticationError("Account not active, please email us")

        if result["used_data"] > result["data_cap"]:
            raise AuthenticationError("Data cap reached")

        request.state.max_upload = (
            result["max_upload"]
            if result["max_upload"] else Config.max_size
        )

        return AuthCredentials(["authenticated"]), SimpleUser(username)
