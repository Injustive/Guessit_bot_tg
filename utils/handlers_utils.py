import asyncio
from contextlib import suppress

from aiogram import types
from aiogram.utils.exceptions import (MessageCantBeDeleted,
                                      MessageToDeleteNotFound)


async def delete_message(message: types.Message, sleep_time=0):
    await asyncio.sleep(sleep_time)
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await message.delete()