from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request

from ..resources import Config


class PremiumPage(HTTPEndpoint):
    async def get(self, request: Request):
        return Config.template.TemplateResponse(
            "premium.html",
            {
                "request": request
            }
        )
