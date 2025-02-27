from aiogram import Router, types
from aiogram.filters import Command
from bot.db.database import Database
from bot.services.google_sheets import fetch_google_sheet_data

router = Router()
db = Database()

async def update_events_from_sheets():
    """Обновляет события из Google Sheets"""
    try:
        events_data = fetch_google_sheet_data()
        db.update_events(events_data)
        return True, "Данные успешно обновлены"
    except Exception as e:
        return False, f"Ошибка при обновлении данных: {str(e)}"

@router.message(Command("update_events"))
async def update_events_command(message: types.Message):
    """Обработчик секретной команды для обновления данных"""
    # Можно добавить проверку на администратора
    if message.from_user.id == 460014703:  # Замените на ваш ID администратора
        success, response = await update_events_from_sheets()
        await message.answer(response)
    else:
        await message.answer("У вас нет прав для выполнения этой команды")

def register_data_updater_handlers(dp):
    dp.include_router(router)