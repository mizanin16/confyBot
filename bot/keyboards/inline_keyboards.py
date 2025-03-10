from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List

def create_inline_keyboard(
        items: List[str],
        callback_prefix: str,
        row_width: int = 2
) -> InlineKeyboardMarkup:
    """
    Создаёт инлайн-клавиатуру с динамическими элементами.

    :param items: Список текстов кнопок
    :param callback_prefix: Префикс для callback data
    :param row_width: Количество кнопок в строке
    :return: InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()
    for item in items:
        builder.add(InlineKeyboardButton(
            text=item,
            callback_data=f"{callback_prefix}:{item}"
        ))
    builder.adjust(row_width)
    return builder.as_markup()

def get_theme_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора тематики мероприятий."""
    themes = [
        "Реклама, маркетинг, PR",
        "IT, разработка",
        "E-COM",
    ]
    builder = InlineKeyboardBuilder()
    for theme in themes:
        builder.button(text=theme, callback_data=f"theme:{theme}")
    builder.row(InlineKeyboardButton(text="Показать все", callback_data="theme:Показать все"))
    return builder.as_markup()

def get_date_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора даты мероприятий."""
    builder = InlineKeyboardBuilder()
    builder.button(text="📅 Выбрать дату", callback_data="custom_input")
    builder.button(text="📆 Выбрать диапазон", callback_data="custom_range_input")
    builder.adjust(1)
    return builder.as_markup()

def get_geo_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора местоположения мероприятий."""
    locations = ["Москва", "Санкт-Петербург", "Показывать все"]
    return create_inline_keyboard(locations, "geo")

def get_cost_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для фильтрации по стоимости мероприятий."""
    cost_filters = [
        "Бесплатно",
        "До 10.000 рублей",
        "От 10.000 рублей",
        "Показывать все"
    ]
    return create_inline_keyboard(cost_filters, "cost")

def get_format_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора формата мероприятий."""
    formats = ["Показывать все", "Только офлайн", "Только онлайн"]
    return create_inline_keyboard(formats, "format")

def get_subscriptions_keyboard(subscriptions) -> InlineKeyboardMarkup:
    """Создаёт клавиатуру с подписками, где название некликабельно, а рядом кнопки 'Удалить' и 'Поиск'"""
    builder = InlineKeyboardBuilder()
    for sub_id, sub_name in subscriptions:
        # Добавляем название подписки как текст (без callback)
        builder.button(text=f"{sub_name}", callback_data="ignore")  # "ignore" делает кнопку некликабельной
        builder.button(text="🗑", callback_data=f"delete_sub:{sub_id}")
        builder.button(text="🔍", callback_data=f"search_sub:{sub_id}")
        builder.adjust(3)  # Три элемента в строке: название, удалить, поиск
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main"))
    return builder.as_markup()

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню без кнопки 'Поиск мероприятий'"""
    builder = InlineKeyboardBuilder()
    builder.button(text="📌 Добавить подписку", callback_data="add_subscription")
    builder.button(text="📜 Мои подписки", callback_data="view_subscriptions")
    builder.button(text="⚙️ Настройки", callback_data="settings")
    builder.adjust(1)
    return builder.as_markup()