from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.datastructures import UploadFile
from starlette.authentication import requires

from ...helpers.upload import upload_file
from ...responses import error_response, response
from ...resources import Sessions


class UploadAPI(HTTPEndpoint):
    @requires("authenticated")
    async def post(self, request: Request) -> JSONResponse:
        form = await request.form()

        if "upload" not in form or not isinstance(form["upload"], UploadFile):
            return error_response("upload fields missing", status_code=422)

        file_id = ""
        user_key = b""
        content_length = 0

        async for _, file_id, user_key, content_length in upload_file(form, request.state.max_upload):
            pass

        await Sessions.mongo.api.update_one(
            {"username": request.user.display_name},
            {
                "$inc": {"used_data": content_length},
                "$push": {"file_ids": file_id},
            },
            upsert=True
        )

        return response({
            "file_id": file_id,
            "password": user_key.decode()
        })
