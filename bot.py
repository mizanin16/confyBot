from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram.utils.token import TokenValidationError
from config import BOT_TOKEN
from handlers.start import register_start_handler

async def main():
    try:
        # Создаём бота и диспетчер
        bot = Bot(token=BOT_TOKEN)
        dp = Dispatcher(storage=MemoryStorage())

        # Регистрация обработчиков
        register_start_handler(dp)

        # Устанавливаем команды бота
        await bot.set_my_commands([
            BotCommand(command="start", description="Запустить бота"),
        ])

        # Запуск поллинга
        await dp.start_polling(bot)

    except TokenValidationError:
        print("Ошибка: Укажите валидный токен бота в файле config.py.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
