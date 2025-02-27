from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.states.filter_states import FilterStates
from bot.keyboards.inline_keyboards import get_theme_keyboard, get_geo_keyboard
from bot.handlers.filters.common import add_custom_input_button

router = Router()


async def set_filter_name(message: types.Message, state: FSMContext):
    """ Добавляет наименование подписки """

    await message.answer("Назовите вашу подписку?\n(например, 'Мероприятия в августе по рекламе в МСК')")
    await state.set_state(FilterStates.question)


@router.message(FilterStates.question)
async def filter_question(message: types.Message, state: FSMContext):
    """Processes user's topic of interest and moves to theme selection"""
    print(message.text)
    await state.update_data(question=message.text)
    keyboard = add_custom_input_button(get_theme_keyboard())
    await message.answer(
        "Выберите тематику мероприятия:",
        reply_markup=keyboard,

    )
    print(message.text)

    await state.set_state(FilterStates.theme)


@router.callback_query(FilterStates.theme, F.data.startswith("theme:"))
async def filter_theme(callback: types.CallbackQuery, state: FSMContext):
    selected_theme = callback.data.split(":")[1]
    user_data = await state.get_data()
    print(selected_theme)
    themes = user_data.get("themes", [])
    # если выбрана тема "Показать все" - очистить все выбранные раннее темы
    if selected_theme in themes:
        if "Показать все" in selected_theme and "Показать все" in themes:
            themes = []
        else:
            themes.remove(selected_theme)
    else:
        if "Показать все" in selected_theme:
            themes = [selected_theme]
        else:
            if "Показать все" in themes:
                themes.remove("Показать все")
            themes.append(selected_theme)

    await state.update_data(themes=themes)
    selected_text = "\n".join(themes) if themes else "Ничего не выбрано"
    keyboard = add_custom_input_button(get_theme_keyboard())
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_theme")])

    await callback.message.edit_text(
        f"Выбраны тематики:\n{selected_text}\n\nВыберите дополнительные или подтвердите выбор:",
        reply_markup=keyboard
    )


@router.message(FilterStates.theme_custom)
async def process_custom_theme(message: types.Message, state: FSMContext):
    """Обрабатывает пользовательский ввод тематики"""
    user_theme = message.text.strip()

    if not user_theme:
        await message.answer("Введите корректное значение.")
        return

    user_data = await state.get_data()
    themes = user_data.get("themes", [])

    themes.append(user_theme)
    await state.update_data(themes=themes)

    selected_text = "\n".join(themes) if themes else "Ничего не выбрано"
    keyboard = add_custom_input_button(get_theme_keyboard())
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_theme")])

    await message.answer(
        f"Выбраны тематики:\n{selected_text}\n\nВыберите дополнительные или подтвердите выбор:",
        reply_markup=keyboard
    )
    await state.set_state(FilterStates.theme)


@router.callback_query(FilterStates.question, F.data == "custom_input")
async def theme_custom_input(callback: types.CallbackQuery, state: FSMContext):
    """Handles request for custom theme input"""
    await callback.message.edit_text("Введите свою тематику:")
    await state.set_state(FilterStates.theme_custom)


@router.callback_query(FilterStates.theme, F.data == "custom_input")
async def theme_custom_input(callback: types.CallbackQuery, state: FSMContext):
    """Переход в режим ввода своей тематики"""
    await callback.message.edit_text("Введите свою тематику:")
    await state.set_state(FilterStates.theme_custom)


@router.callback_query(FilterStates.theme, F.data == "confirm_theme")
async def confirm_theme(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    themes = user_data.get("themes", [])
    await state.update_data(theme=", ".join(themes))
    keyboard = add_custom_input_button(get_geo_keyboard())
    await callback.message.edit_text(
        f"Выбраны тематики: {', '.join(themes)}\n\nВыберите гео мероприятия:",
        reply_markup=keyboard
    )
    await state.set_state(FilterStates.geo)


def register_category_handlers(dp):
    dp.include_router(router)
