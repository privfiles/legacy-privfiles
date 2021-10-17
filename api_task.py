import asyncio
import time

from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient


async def check() -> None:
    mongo = AsyncIOMotorClient()
    db = mongo.privfiles

    await db.api.update_many(
        {
            "active": True,
            "next_payment": {"$lte": datetime.now()}
        },
        {"$set": {
            "active": False,
            "next_payment": None
        }}
    )

    print("Deactivated expired accounts")


loop = asyncio.get_event_loop()
while True:
    loop.run_until_complete(check())
    time.sleep(43200)
