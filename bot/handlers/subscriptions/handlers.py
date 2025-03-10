import logging
from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.db.queries import delete_subscription, get_filter_details
from bot.handlers.subscriptions.utils import show_user_subscriptions
from bot.keyboards.inline_keyboards import get_main_menu_keyboard
from bot.services.event_service import EventService
from bot.db.database import Database

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()
event_service = EventService(Database())

# Количество событий на странице
EVENTS_PER_PAGE = 5


def get_paginated_keyboard(total_events: int, page: int, subscription_id: int) -> InlineKeyboardMarkup:
    """Создаёт клавиатуру с пагинацией"""
    builder = InlineKeyboardBuilder()
    total_pages = (total_events + EVENTS_PER_PAGE - 1) // EVENTS_PER_PAGE

    if page > 1:
        builder.button(text="⬅️ Назад", callback_data=f"search_sub:{subscription_id}:{page - 1}")
    if page < total_pages:
        builder.button(text="Далее ➡️", callback_data=f"search_sub:{subscription_id}:{page + 1}")
    builder.button(text="🔙 В главное меню", callback_data="back_to_main")

    builder.adjust(2 if page > 1 and page < total_pages else 1)
    return builder.as_markup()


@router.callback_query(F.data == "view_subscriptions")
async def view_subscriptions(callback: types.CallbackQuery):
    """Обработчик кнопки 'Мои подписки'"""
    logger.info(f"User {callback.from_user.id} pressed 'view_subscriptions'")
    await show_user_subscriptions(callback)


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    """Возвращает пользователя в главное меню"""
    logger.info(f"User {callback.from_user.id} pressed 'back_to_main'")
    await callback.message.edit_text("👋 Добро пожаловать в главное меню!", reply_markup=get_main_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data.startswith("delete_sub:"))
async def delete_subscription_handler(callback: types.CallbackQuery):
    """Удаляет подписку и обновляет список"""
    subscription_id = int(callback.data.split(":")[1])
    logger.info(f"User {callback.from_user.id} deleting subscription {subscription_id}")
    delete_subscription(subscription_id)
    await callback.answer("✅ Подписка удалена.")
    await show_user_subscriptions(callback)


@router.callback_query(F.data.startswith("search_sub:"))
async def search_subscription_events(callback: types.CallbackQuery):
    """Поиск мероприятий по выбранной подписке с пагинацией"""
    data = callback.data.split(":")
    subscription_id = int(data[1])
    page = int(data[2]) if len(data) > 2 else 1  # Номер страницы, по умолчанию 1

    logger.info(f"User {callback.from_user.id} searching events for subscription {subscription_id}, page {page}")

    sub_details = get_filter_details(subscription_id)
    if not sub_details:
        logger.warning(f"Subscription {subscription_id} not found")
        await callback.message.edit_text("❌ Подписка не найдена.", reply_markup=get_main_menu_keyboard())
        await callback.answer()
        return

    # Поиск мероприятий
    events = event_service.find_events_by_filter(
        subscription_name=sub_details["subscription_name"],
        category=sub_details["category"],
        date=sub_details["date"],
        cost=sub_details["cost"].replace('.', ''),
        format=sub_details["format"],
        location=sub_details["location"]
    )
    logger.info(f"Found {len(events)} events for subscription {subscription_id}")

    if not events:
        text = f"😕 По подписке '{sub_details['subscription_name']}' ничего не найдено."
        keyboard = get_main_menu_keyboard()
    else:
        # Вычисляем диапазон событий для текущей страницы
        start_idx = (page - 1) * EVENTS_PER_PAGE
        end_idx = min(start_idx + EVENTS_PER_PAGE, len(events))
        paginated_events = events[start_idx:end_idx]

        text = f"📋 Мероприятия по подписке '{sub_details['subscription_name']}' (страница {page} из {(len(events) + EVENTS_PER_PAGE - 1) // EVENTS_PER_PAGE}):\n\n"
        for i, event in enumerate(paginated_events, start_idx + 1):
            text += (
                f"{i}. **{event['title']}**\n"
                f"📅 {event['date']}\n"
                f"🌍 {event['location']}\n"
                f"💰 {event['cost']}\n"
                f"📌 {event['format']}\n"
                f"🔗 {event['url']}\n\n"
            )
        keyboard = get_paginated_keyboard(len(events), page, subscription_id)

    try:
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        await callback.answer()
    except Exception as e:
        if "MESSAGE_TOO_LONG" in str(e):
            logger.error(f"Message too long even with pagination: {len(text)} characters")
            await callback.message.edit_text(
                "Слишком много данных для отображения. Попробуйте уточнить фильтры.",
                reply_markup=get_main_menu_keyboard()
            )
            await callback.answer()
        else:
            raise
