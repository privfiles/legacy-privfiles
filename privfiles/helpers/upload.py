import asyncio
from typing import AsyncGenerator, Tuple

from starlette.datastructures import UploadFile, FormData

from backblaze.settings import PartSettings, UploadSettings
from backblaze.exceptions import InternalError

from cryptography.fernet import Fernet
from secrets import token_urlsafe

from ..resources import Config, Sessions
from ..errors import (
    CommentLengthError,
    ContentLengthError,
    ZeroContentLengthError
)


async def upload_file(form: FormData, max_upload: int = None,
                      local_dencrypt: bool = False,
                      ) -> AsyncGenerator[Tuple[bool, str, bytes, int], None]:
    """Used to upload encrypted data.

    Parameters
    ----------
    form : FormData
    max_upload : int, optional
        If None uses default max_size, by default None
    local_dencrypt : bool, optional
        by default False

    Yields
    ------
    bool
        If upload completed
    str
        file_id
    bytes
        fernet key
    int
        content length, will be the current uploaded length if not completed

    Raises
    ------
    CommentLengthError
    ZeroContentLengthError
    """

    if max_upload is None:
        max_upload = Config.size.max_size

    if "comment" in form:
        if len(form["comment"]) > 1000:
            raise CommentLengthError()

        comment = form["comment"]
    else:
        comment = None

    key = Fernet.generate_key()
    fer = Fernet(key)
    file_id = token_urlsafe(64)
    user_key = Fernet.generate_key()

    upload_file: UploadFile = form["upload"]  # type: ignore

    # We don't really care about the name of the file
    # in storage
    never_stored_file_id = token_urlsafe(64)

    model, file = await Sessions.bucket.create_part(
        PartSettings(never_stored_file_id)
    )

    parts = file.parts()

    data = True
    next_index = 0
    encrypted_chunk_len = 0
    content_length = 0
    while data:
        await upload_file.seek(next_index)

        data = await upload_file.read(Config.size.read_size)
        if data:
            content_length += len(data)

            if content_length > max_upload:
                try:
                    await file.cancel()
                except InternalError:
                    pass

                raise ContentLengthError()

            e_data = fer.encrypt(
                data if isinstance(data, bytes) else data.encode()
            )

            if (not encrypted_chunk_len and
                    content_length < Config.size.read_size):
                break

            if not encrypted_chunk_len:
                encrypted_chunk_len = len(e_data)

            await parts.data(e_data)

            yield False, file_id, user_key, content_length

            next_index += Config.size.read_size

            await asyncio.sleep(0.01)

    if content_length == 0:
        try:
            await file.cancel()
        except InternalError:
            pass

        raise ZeroContentLengthError()
    elif parts.part_number == 0 and data:
        try:
            await file.cancel()
        except InternalError:
            pass

        model, file = await Sessions.bucket.upload(UploadSettings(
            never_stored_file_id
        ), e_data)
    else:
        await parts.finish()

    await Sessions.mongo.files.insert_one({
        "file_id": file_id,
        "real_file_name": fer.encrypt(upload_file.filename.encode()),
        "real_content_type": fer.encrypt(
            upload_file.content_type.encode()
        ),
        "real_content_length": fer.encrypt(
            str(content_length).encode()
        ),
        "external_id": fer.encrypt(model.file_id.encode()),
        "chunk": fer.encrypt(str(encrypted_chunk_len).encode()),
        "password": Fernet(user_key).encrypt(key),
        "comment": comment,
        "local_dencrypt": local_dencrypt,
        "downloads": 0
    })

    yield True, file_id, user_key, content_length
