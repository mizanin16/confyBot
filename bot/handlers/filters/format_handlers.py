from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.states.filter_states import FilterStates
from bot.keyboards.inline_keyboards import get_cost_keyboard
from bot.handlers.filters.common import add_custom_input_button
from bot.handlers.filters.confirm_handlers import confirm_selection

router = Router()


@router.callback_query(FilterStates.format, F.data.startswith("format:"))
async def filter_format(callback: types.CallbackQuery, state: FSMContext):
    format = callback.data.split(":")[1]
    await state.update_data(format=format)
    await confirm_selection(callback, state)
