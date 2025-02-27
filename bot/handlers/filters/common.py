from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def add_custom_input_button(keyboard: InlineKeyboardMarkup) -> InlineKeyboardMarkup:
    """Add a 'Custom Input' button to any inline keyboard"""
    builder = InlineKeyboardBuilder()
    for row in keyboard.inline_keyboard:
        for button in row:
            builder.add(button)
    builder.adjust(len(keyboard.inline_keyboard[0]))
    builder.row(InlineKeyboardButton(
        text="✏️ Ввести своё значение",
        callback_data="custom_input"
    ))
    return builder.as_markup()

