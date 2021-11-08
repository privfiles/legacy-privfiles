import backblaze
import sys

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware

from motor.motor_asyncio import AsyncIOMotorClient

from multicolorcaptcha import CaptchaGenerator

from .resources import Sessions, Config
from .key_loader import KeyLoader
from .settings import B2Settings, CaptchaSettings, MongoSettings, SizeSettings
from .middleware import BasicAuthBackend

from .routes import ROUTES, ERROR_HANDLERS
from .routes.errors import on_auth_error


class PrivFiles(Starlette):
    def __init__(self, backblaze_settings: B2Settings,
                 captcha_settings: CaptchaSettings = CaptchaSettings(),
                 mongo_settings: MongoSettings = MongoSettings(),
                 size_settings: SizeSettings = SizeSettings(),
                 **kwargs) -> None:
        """Used to configure privfiles.

        Parameters
        ----------
        backblaze_settings : B2Settings
        captcha_settings : CaptchaSettings, optional
            by default CaptchaSettings()
        mongo_settings : MongoSettings, optional
            by default MongoSettings()
        size_settings : MongoSettings, optional
            by default SizeSettings()
        """

        self.__backblaze_settings = backblaze_settings
        self.__mongo_settings = mongo_settings

        Config.captcha = captcha_settings
        Config.size = size_settings

        # Needed middlewares
        middlewares = [
            Middleware(
                SessionMiddleware,
                secret_key=KeyLoader(name="session").load()
            ),
            Middleware(
                AuthenticationMiddleware,
                backend=BasicAuthBackend(),
                on_error=on_auth_error
            )
        ]

        # Check if any used kwargs passed
        if "middleware" in kwargs:
            middlewares += kwargs["middleware"]
            kwargs.pop("middleware")

        if "routes" in kwargs:
            routes = kwargs["routes"] + ROUTES
            kwargs.pop("routes")
        else:
            routes = ROUTES

        if "exception_handlers" in kwargs:
            exception_handlers = {
                **kwargs["exception_handlers"],
                **ERROR_HANDLERS
            }
            kwargs.pop("exception_handlers")
        else:
            exception_handlers = ERROR_HANDLERS

        startup_tasks = [self._startup]
        shutdown_tasks = [self._shutdown]

        if "on_startup" in kwargs:
            startup_tasks += kwargs["on_startup"]
            kwargs.pop("on_startup")

        if "on_shutdown" in kwargs:
            shutdown_tasks += kwargs["on_shutdown"]
            kwargs.pop("on_shutdown")

        super().__init__(
            routes=routes,
            middleware=middlewares,
            exception_handlers=exception_handlers,  # type: ignore
            on_startup=startup_tasks,
            on_shutdown=shutdown_tasks,
            **kwargs
        )

    async def _startup(self) -> None:
        """Starts sessions
        """

        Sessions.captcha = CaptchaGenerator(Config.captcha.size)

        mongo = AsyncIOMotorClient(self.__mongo_settings.connection)

        try:
            await mongo.server_info()
        except Exception:
            sys.exit("No mongo connection")

        Sessions.mongo = mongo[self.__mongo_settings.database]

        self.__b2 = backblaze.Awaiting(
            self.__backblaze_settings.key_id,
            self.__backblaze_settings.application_key,
            timeout=720
        )

        await self.__b2.authorize()

        Sessions.bucket = self.__b2.bucket(self.__backblaze_settings.bucket_id)

    async def _shutdown(self) -> None:
        """Closes created sessions.
        """

        await self.__b2.close()
