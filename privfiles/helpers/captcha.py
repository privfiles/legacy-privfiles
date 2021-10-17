from bcrypt import hashpw, gensalt, checkpw
from starlette.requests import Request


def validate_captcha(request: Request, given_cap: str) -> bool:
    if "captcha" not in request.session:
        return False

    hashed_answer = hashpw(
        request.session["captcha"].encode(),
        gensalt()
    )

    request.session.pop("captcha")

    return checkpw(given_cap.lower().encode(), hashed_answer)
