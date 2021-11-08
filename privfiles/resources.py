import os
from os import path

from starlette.templating import Jinja2Templates
from backblaze.bucket.awaiting import AwaitingBucket
from motor.motor_asyncio import AsyncIOMotorClient
from multicolorcaptcha import CaptchaGenerator

from .settings import CaptchaSettings, SizeSettings


class Sessions:
    captcha: CaptchaGenerator
    bucket: AwaitingBucket
    mongo: AsyncIOMotorClient


class Config:
    project_dir = os.path.dirname(os.path.realpath(__file__))
    template = Jinja2Templates(directory=path.join(project_dir, "templates"))
    captcha: CaptchaSettings
    size: SizeSettings
