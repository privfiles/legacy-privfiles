from typing import Tuple
from cryptography.fernet import Fernet

from ..resources import Sessions
from ..errors import FileIdError, PasswordError


async def delete_upload(password: str, file_id: str) -> Tuple[dict, Fernet]:
    result = await Sessions.mongo.files.find_one({
        "file_id": file_id
    })
    if not result:
        raise FileIdError()

    try:
        fer = Fernet(
            Fernet(password.encode()).decrypt(
                result["password"]
            )
        )

        b2_file_id = (fer.decrypt(result["external_id"])).decode()
    except Exception:
        raise PasswordError()

    await Sessions.mongo.files.delete_one({
        "file_id": file_id
    })

    await Sessions.bucket.file(b2_file_id).delete()

    return result, fer
