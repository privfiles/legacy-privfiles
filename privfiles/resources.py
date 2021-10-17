import os
from os import path

from captcha.image import ImageCaptcha
from starlette.templating import Jinja2Templates
from backblaze.bucket.awaiting import AwaitingBucket
from motor.motor_asyncio import AsyncIOMotorClient


class Sessions:
    captcha: ImageCaptcha
    bucket: AwaitingBucket
    mongo: AsyncIOMotorClient


class Config:
    project_dir = os.path.dirname(os.path.realpath(__file__))
    template = Jinja2Templates(directory=path.join(project_dir, "templates"))
    read_size = 5000024
    max_size = 943700000
