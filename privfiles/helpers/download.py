import asyncio

from urllib.parse import quote
from typing import AsyncGenerator
from cryptography.fernet import Fernet
from backblaze.settings import DownloadSettings

from starlette.responses import StreamingResponse

from ..resources import Config, Sessions
from ..errors import PasswordError


async def decrypt_file(upload_chunk_size: int,
                       file_fer: Fernet,
                       external_id: str) -> AsyncGenerator[bytes, None]:
    file_ = Sessions.bucket.file(external_id)

    model = await file_.get()
    if model.content_length < Config.size.read_size:
        yield file_fer.decrypt(await file_.download())
    else:
        next_index = upload_chunk_size
        last_index = 0
        while True:
            data = await file_.download(
                DownloadSettings(range=f"bytes={last_index}-{next_index}")
            )

            if data:
                yield file_fer.decrypt(data)

                next_index += upload_chunk_size
                last_index += upload_chunk_size

                if last_index >= model.content_length:
                    break

            await asyncio.sleep(0.01)


async def stream_response(file_id: str, password: str
                          ) -> StreamingResponse:
    result = await Sessions.mongo.files.find_one({
        "file_id": file_id
    })

    if not result:
        raise PasswordError()

    try:
        user_fer = Fernet(password.encode())
    except Exception:
        raise PasswordError()

    try:
        file_fer = Fernet(user_fer.decrypt(result["password"]))
    except Exception:
        raise PasswordError()

    await Sessions.mongo.files.update_one(
        {"file_id": file_id},
        {
            "$inc": {"downloads": 1},
        },
        upsert=True
    )

    file_name = quote(file_fer.decrypt(result["real_file_name"]).decode())

    return StreamingResponse(
        decrypt_file(
            int(file_fer.decrypt(result["chunk"]).decode()),
            file_fer,
            file_fer.decrypt(result["external_id"]).decode()
        ),
        media_type=file_fer.decrypt(
            result["real_content_type"]
        ).decode(),
        headers={
            "Content-Disposition": f'attachment; filename*=UTF-8\'\'{file_name}',  # noqa: E501
            "Content-Length": file_fer.decrypt(
                result["real_content_length"]
            ).decode()
        }
    )
