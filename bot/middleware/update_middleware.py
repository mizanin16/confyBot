from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from bot.handlers.data_updater import update_events_from_sheets
import asyncio
import time


class DataUpdateMiddleware(BaseMiddleware):
    def __init__(self):
        self.last_update = 0
        self.update_interval = 7*86_400  # Обновление раз в час

    async def __call__(self, handler, event: TelegramObject, data: dict):
        current_time = time.time()

        if current_time - self.last_update >= self.update_interval:
            success, message = await update_events_from_sheets()
            self.last_update = current_time
            print(f"Auto-update: {message}")

        return await handler(event, data)


