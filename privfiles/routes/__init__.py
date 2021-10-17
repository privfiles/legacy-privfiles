from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.exceptions import HTTPException

from os import path
from ..resources import Config

# Routes
from .captcha import CaptchaGen
from .pages import (
    HomePage,
    SharePage,
    StorageAPIPage,
    ReportPage,
    AdvertisePage,
    ZeroPage,
    TestCaptcha
)
from .upload import UploadEncryptFile
from .download import DownloadDecryptFile
from .account import AccountGenerate, AccountPage

# API routes
from .api.upload import UploadAPI
from .api.download import DownloadAPI
from .api.misc import AccountAPI, DeleteAPI

# Admin shit
from .admin import AdminPage, AdminUpdateAccount

# Errors
from .errors import on_privfile_error, on_http_error, PrivFilesError


ROUTES = [
    Route("/generate-captcha", CaptchaGen, name="captcha"),
    Route("/test-captcha", TestCaptcha, name="testcaptcha"),
    Route("/upload", UploadEncryptFile, name="upload"),
    Route("/download/{file_id}", DownloadDecryptFile, name="download"),
    Mount("/share", routes=[
        Route("/{file_id}/{share_password}", SharePage, name="sharewithpass"),
        Route("/{file_id}", SharePage, name="share"),
    ]),
    Route("/report", ReportPage),
    Route("/advertise", AdvertisePage),
    Route("/storage-api", StorageAPIPage),
    Route("/generate-account", AccountGenerate),
    Route("/zero", ZeroPage),
    Route("/account", AccountPage),
    Mount(
        "/static",
        StaticFiles(directory=path.join(Config.project_dir, "static")),
        name="static"
    ),
    Mount("/admin", routes=[
        Route("/", AdminPage),
        Route("/account-update", AdminUpdateAccount)
    ]),
    Mount("/api", routes=[
        Route("/upload", UploadAPI),
        Route("/account", AccountAPI),
        Route("/download/{file_id}", DownloadAPI),
        Route("/delete/{file_id}", DeleteAPI)
    ]),
    Route("/", HomePage)
]

ERROR_HANDLERS = {
    PrivFilesError: on_privfile_error,
    HTTPException: on_http_error
}
