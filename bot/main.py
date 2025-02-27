import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram.client.default import DefaultBotProperties
from bot.handlers import register_all_handlers
from bot.config import BOT_TOKEN
from bot.services.notification_service import schedule_notifications
from bot.middleware.update_middleware import DataUpdateMiddleware
from bot.services.event_service import EventService
from bot.db.queries import Database

async def set_bot_commands(bot: Bot):
    """
    Set bot commands in Telegram interface.
    """
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Справка по боту"),
        BotCommand(command="settings", description="Настройка"),
    ]
    await bot.set_my_commands(commands)


async def main():
    """
    Main bot startup routine.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    try:
        bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
        dp = Dispatcher(storage=MemoryStorage())
        db = Database()
        dp.message.middleware(DataUpdateMiddleware())
        await set_bot_commands(bot)
        register_all_handlers(dp)
        event_service = EventService(db)
        asyncio.create_task(schedule_notifications(bot, event_service))
        logger.info("Starting bot...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())
