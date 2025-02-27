from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.states.filter_states import FilterStates
from bot.keyboards.inline_keyboards import get_geo_keyboard, get_date_keyboard
from bot.handlers.filters.common import add_custom_input_button

router = Router()


@router.callback_query(FilterStates.geo, F.data == "custom_input")
async def geo_custom_input(callback: types.CallbackQuery, state: FSMContext):
    """Handles request for custom geo input"""
    await callback.message.edit_text("Введите своё местоположение:")
    await state.set_state(FilterStates.geo_custom)


@router.message(FilterStates.geo_custom)
async def process_custom_geo(message: types.Message, state: FSMContext):
    """Processes custom geo input"""
    await state.update_data(geo=message.text)
    keyboard = add_custom_input_button(get_date_keyboard())
    await message.answer(
        f"Выбрано гео: {message.text}\n\nВыберите даты проведения:",
        reply_markup=keyboard
    )
    await state.set_state(FilterStates.date)


@router.callback_query(FilterStates.geo, F.data.startswith("geo:"))
async def filter_geo(callback: types.CallbackQuery, state: FSMContext):
    geo = callback.data.split(":")[1]
    await state.update_data(geo=geo)
    keyboard = add_custom_input_button(get_date_keyboard())
    await callback.message.edit_text(
        f"Выбрано гео: {geo}\n\nВыберите даты проведения:",
        reply_markup=keyboard
    )
    await state.set_state(FilterStates.date)


def register_location_handlers(dp):
    dp.include_router(router)
