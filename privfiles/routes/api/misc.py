from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.authentication import requires

from ...responses import error_response, response
from ...resources import Config, Sessions
from ...errors import FileIdError
from ...helpers.delete import delete_upload


class AccountAPI(HTTPEndpoint):
    @requires("authenticated")
    async def get(self, request: Request) -> JSONResponse:
        result = await Sessions.mongo.api.find_one({
            "username": request.user.display_name
        })

        return response({
            "storage_used": result["used_data"],
            "storage_capacity": result["data_cap"],
            "max_upload": result["max_upload"]
            if result["max_upload"] else Config.size.max_size,
            "next_payment": result["next_payment"].timestamp()
            if result["next_payment"] else None,
            "file_ids": result["file_ids"]
        })


class DeleteAPI(HTTPEndpoint):
    @requires("authenticated")
    async def delete(self, request: Request) -> JSONResponse:
        form = await request.form()

        if "password" not in form:
            return error_response("Password is required", status_code=422)

        result = await Sessions.mongo.api.find_one({
            "username": request.user.display_name,
            "file_ids": {"$in": [request.path_params["file_id"]]}
        })
        if not result:
            raise FileIdError()

        file_result, fer = await delete_upload(
            form["password"], request.path_params["file_id"]
        )

        await Sessions.mongo.api.update_one(
            {"username": request.user.display_name},
            {
                "$pull": {
                    "file_ids": {"$in": [request.path_params["file_id"]]}
                },
                "$inc": {"used_data": -abs(int(
                    (fer.decrypt(file_result["real_content_length"])).decode()
                ))}
            }
        )

        return response()
