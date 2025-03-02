from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from bot.db.queries import get_filtered_events, get_user_filters, get_filter_details, get_filter_by_name
from bot.keyboards.inline_keyboards import get_main_menu_keyboard
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()


@router.callback_query(F.data == "search_events")
async def search_events_start(callback: types.CallbackQuery):
    """Начинает процесс поиска мероприятий"""
    user_id = callback.from_user.id

    # Получаем подписки пользователя
    from bot.db.queries import get_user_subscriptions
    subscriptions = get_user_subscriptions(user_id)

    if not subscriptions:
        await callback.message.edit_text(
            "У вас пока нет сохраненных фильтров. Сначала добавьте подписку с фильтрами.",
            reply_markup=get_main_menu_keyboard()
        )
        return

    # Создаем клавиатуру с подписками для выбора фильтра
    keyboard = []
    for sub_id, sub_name in subscriptions:
        keyboard.append([
            InlineKeyboardButton(text=sub_name, callback_data=f"search_by_filter:{sub_id}")
        ])

    # Добавляем кнопку возврата
    keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")])

    await callback.message.edit_text(
        "Выберите фильтр для поиска мероприятий:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )


@router.callback_query(F.data.startswith("search_by_filter:"))
async def search_with_filter(callback: types.CallbackQuery):
    """Поиск мероприятий по выбранному фильтру"""
    filter_id = int(callback.data.split(":")[1])

    # Получаем детали фильтра
    filter_details = get_filter_details(filter_id)

    if not filter_details:
        await callback.message.edit_text(
            "Не удалось найти указанный фильтр. Попробуйте снова.",
            reply_markup=get_main_menu_keyboard()
        )
        return

    # Выполняем поиск мероприятий с выбранным фильтром
    events = get_filtered_events(filter_details)

    if not events:
        # Создаем сообщение с деталями использованного фильтра
        filter_text = (
            f"📋 <b>Параметры поиска:</b>\n"
            f"📜 <b>Запрос:</b> {filter_details['subscription_name']}\n"
            f"🌟 <b>Тематика:</b> {filter_details['category']}\n"
            f"📅 <b>Дата:</b> {filter_details['date']}\n"
            f"💰 <b>Стоимость:</b> {filter_details['cost']}\n"
            f"📌 <b>Формат:</b> {filter_details['format']}\n"
            f"🌍 <b>Местоположение:</b> {filter_details['location']}\n\n"
            f"😕 <b>Мероприятий по выбранным параметрам не найдено.</b>"
        )

        keyboard = [
            [InlineKeyboardButton(text="🔎 Изменить фильтры", callback_data="search_events")],
            [InlineKeyboardButton(text="🔙 В главное меню", callback_data="back_to_main")]
        ]

        await callback.message.edit_text(
            filter_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode="HTML"
        )
        return

    # Отображаем результаты
    await display_events(callback, events, filter_details)


async def display_events(callback: types.CallbackQuery, events: list, filter_details: dict):
    """Отображает найденные мероприятия"""
    # Ограничиваем количество мероприятий в одном сообщении
    max_events_per_message = 5
    events_count = len(events)

    # Создаем заголовок с информацией о фильтрах
    header = (
        f"📋 <b>Найдено мероприятий:</b> {events_count}\n"
        f"📜 <b>Запрос:</b> {filter_details['subscription_name']}\n"
        f"🌟 <b>Тематика:</b> {filter_details['category']}\n"
        f"📅 <b>Дата:</b> {filter_details['date']}\n"
        f"💰 <b>Стоимость:</b> {filter_details['cost']}\n"
        f"📌 <b>Формат:</b> {filter_details['format']}\n"
        f"🌍 <b>Местоположение:</b> {filter_details['location']}\n\n"
        f"<b>Результаты поиска:</b>\n\n"
    )

    message_text = header

    # Формируем сообщение с мероприятиями (не больше max_events_per_message)
    events_to_show = events[:max_events_per_message]

    for i, event in enumerate(events_to_show, 1):
        event_text = (
            f"<b>{i}. {event['event_name']}</b>\n"
            f"📅 <b>Дата:</b> {event['event_date']}"
        )

        if event.get('event_time'):
            event_text += f" ⏰ {event['event_time']}"

        event_text += f"\n📍 <b>Место:</b> {event['location']}\n"

        if event.get('description'):
            # Ограничиваем длину описания
            description = event['description']
            if len(description) > 100:
                description = description[:97] + "..."
            event_text += f"📝 {description}\n"

        if event.get('cost'):
            event_text += f"💰 <b>Стоимость:</b> {event['cost']}\n"

        if event.get('event_type'):
            event_text += f"🔍 <b>Формат:</b> {event['event_type']}\n"

        if event.get('event_link'):
            event_text += f"🔗 <a href='{event['event_link']}'>Подробнее</a>\n"

        event_text += "\n"
        message_text += event_text

    # Создаем клавиатуру с кнопками навигации
    keyboard = []

    # Если есть больше мероприятий, добавляем кнопку "Показать еще"
    if events_count > max_events_per_message:
        more_text = f"Показать еще ({events_count - max_events_per_message})"
        keyboard.append([
            InlineKeyboardButton(
                text=more_text,
                callback_data=f"more_events:{filter_details['subscription_name']}:{max_events_per_message}"
            )
        ])

    keyboard.append([InlineKeyboardButton(text="🔎 Другие фильтры", callback_data="search_events")])
    keyboard.append([InlineKeyboardButton(text="🔙 В главное меню", callback_data="back_to_main")])

    await callback.message.edit_text(
        message_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode="HTML",
        disable_web_page_preview=True  # Отключаем предпросмотр для ссылок
    )


@router.callback_query(F.data.startswith("more_events:"))
async def show_more_events(callback: types.CallbackQuery):
    """Показывает следующую порцию мероприятий"""
    parts = callback.data.split(":")
    subscription_name = parts[1]
    offset = int(parts[2])

    filter_details = get_filter_by_name(callback.from_user.id, subscription_name)

    if not filter_details:
        await callback.message.edit_text(
            "Не удалось найти данные фильтра. Попробуйте снова.",
            reply_markup=get_main_menu_keyboard()
        )
        return

    # Получаем мероприятия с заданным смещением
    events = get_filtered_events(filter_details)

    # Определяем количество мероприятий для отображения
    max_events_per_message = 5
    total_events = len(events)

    if offset >= total_events:
        # Если смещение больше общего количества, возвращаемся к началу
        await callback.answer("Вы просмотрели все мероприятия. Возвращаемся к началу списка.")
        await display_events(callback, events, filter_details)
        return

    # Определяем события для показа в текущей порции
    events_to_show = events[offset:offset + max_events_per_message]

    # Формируем заголовок сообщения
    header = (
        f"📋 <b>Найдено мероприятий:</b> {total_events}\n"
        f"<b>Показаны события {offset + 1}-{min(offset + len(events_to_show), total_events)} из {total_events}</b>\n\n"
    )

    message_text = header

    # Добавляем информацию о мероприятиях
    for i, event in enumerate(events_to_show, offset + 1):
        event_text = (
            f"<b>{i}. {event['event_name']}</b>\n"
            f"📅 <b>Дата:</b> {event['event_date']}"
        )

        if event.get('event_time'):
            event_text += f" ⏰ {event['event_time']}"

        event_text += f"\n📍 <b>Место:</b> {event['location']}\n"

        if event.get('description'):
            # Ограничиваем длину описания
            description = event['description']
            if len(description) > 100:
                description = description[:97] + "..."
            event_text += f"📝 {description}\n"

        if event.get('cost'):
            event_text += f"💰 <b>Стоимость:</b> {event['cost']}\n"

        if event.get('event_type'):
            event_text += f"🔍 <b>Формат:</b> {event['event_type']}\n"

        if event.get('event_link'):
            event_text += f"🔗 <a href='{event['event_link']}'>Подробнее</a>\n"

        event_text += "\n"
        message_text += event_text

    # Создаем клавиатуру
    keyboard = []

    # Кнопки навигации
    navigation_row = []

    # Кнопка "Назад" если не на первой странице
    if offset > 0:
        new_offset = max(0, offset - max_events_per_message)
        navigation_row.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"more_events:{subscription_name}:{new_offset}"
            )
        )

    # Кнопка "Вперед" если есть еще мероприятия
    if offset + max_events_per_message < total_events:
        new_offset = offset + max_events_per_message
        navigation_row.append(
            InlineKeyboardButton(
                text="Вперед ➡️",
                callback_data=f"more_events:{subscription_name}:{new_offset}"
            )
        )

    if navigation_row:
        keyboard.append(navigation_row)

    # Добавляем кнопки возврата
    keyboard.append([InlineKeyboardButton(text="🔎 Другие фильтры", callback_data="search_events")])
    keyboard.append([InlineKeyboardButton(text="🔙 В главное меню", callback_data="back_to_main")])

    await callback.message.edit_text(
        message_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode="HTML",
        disable_web_page_preview=True
    )


def register_search_handlers(dp):
    dp.include_router(router)