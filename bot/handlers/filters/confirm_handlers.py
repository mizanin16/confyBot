from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from bot.states.filter_states import FilterStates
from bot.db.queries import save_filters  # Импортируем функцию

router = Router()

async def confirm_selection(callback: types.CallbackQuery, state: FSMContext):
    """Обрабатывает подтверждение выбора фильтров и сохраняет их в БД"""
    user_data = await state.get_data()
    user_id = callback.from_user.id

    subscription_name = user_data.get("question", "Не выбрано")
    date = user_data.get("date", "Не выбрано")
    cost = user_data.get("cost", "Не выбрано")
    format_ = user_data.get("format", "Не выбрано")
    location = user_data.get("geo", "Не выбрано")
    category = user_data.get("theme", "Не выбрано")

    save_filters(user_id, subscription_name, category, date, cost, format_, location)

    response_text = (
        f"✅ Вы выбрали:\n"
        f"📜 Название подписки: {subscription_name}\n"
        f"🌟 Тематики: {category}\n"
        f"📅 Даты: {date}\n"
        f"💰 Стоимость: {cost}\n"
        f"📌 Формат: {format_}\n"
        f"🌍 Местоположение: {location}\n"
        "\nФильтр установлен! Вы можете начать поиск."
    )

    await callback.message.edit_text(response_text)
    await state.clear()

def register_confirm_handlers(dp):
    dp.include_router(router)
