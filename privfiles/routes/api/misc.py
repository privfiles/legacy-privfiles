from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.authentication import requires

from cryptography.fernet import Fernet

from ...responses import error_response, response
from ...resources import Config, Sessions


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
            if result["max_upload"] else Config.max_size,
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
            return error_response("File ID not found", status_code=404)

        file_result = await Sessions.mongo.files.find_one({
            "file_id": request.path_params["file_id"]
        })

        try:
            fer = Fernet(
                Fernet(form["password"].encode()).decrypt(
                    file_result["password"]
                )
            )

            b2_file_id = (fer.decrypt(file_result["external_id"])).decode()
        except Exception:
            return error_response("Invalid password", status_code=400)

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

        await Sessions.mongo.files.delete_one({
            "file_id": request.path_params["file_id"]
        })

        await Sessions.bucket.file(b2_file_id).delete()

        return response()
