from aiogram import Router, types
from aiogram.filters import Command  # Используем новый подход для фильтрации
from services.google_sheets import fetch_google_sheet_data

# Создаём роутер для обработки команд
router = Router()


@router.message(Command("start"))
async def start_command(message: types.Message):
    """
    Обработчик команды /start. Отправляет данные из Google Sheets.
    """
    await message.answer("Привет! Сейчас получу данные из Google Sheets...")

    try:
        data = fetch_google_sheet_data()
        if not data:
            await message.answer("Данные в таблице отсутствуют.")
            return

        # Формируем строку с данными
        for row in data:
            response = "\n".join([f"{key}: {value}" for key, value in row.items() if value]) + "\n"
            await message.answer(response)
    except Exception as e:
        await message.answer(f"Произошла ошибка при получении данных: {e}")


def register_start_handler(dp):
    """
    Регистрация обработчиков команды /start.
    """
    dp.include_router(router)
