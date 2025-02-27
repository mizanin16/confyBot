from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
from bot.states.filter_states import FilterStates
from bot.keyboards.inline_keyboards import get_format_keyboard
from bot.handlers.filters.common import add_custom_input_button

router = Router()


@router.callback_query(FilterStates.cost, F.data == "custom_input")
async def cost_custom_input(callback: types.CallbackQuery, state: FSMContext):
    """Обрабатывает запрос на ввод стоимости вручную"""
    text = "Введите желаемую стоимость:\nПример:\n• 10000-20000\n• От 10000 до 20000\n• До 20000"
    await callback.message.edit_text(text)
    await state.set_state(FilterStates.cost_custom)


@router.message(FilterStates.cost_custom)
async def process_custom_cost(message: types.Message, state: FSMContext):
    """Обрабатывает пользовательский ввод стоимости"""
    cost_text = message.text.strip()

    # Проверка на корректность формата
    if not validate_cost_format(cost_text):
        error_text = ("❌ Неверный формат стоимости.\n"
                      "Используйте один из примеров:\n"
                      "• 10000-20000\n"
                      "• От 10000 до 20000\n"
                      "• До 20000")
        await message.answer(error_text)
        return  # Не переводим состояние, ждём повторного ввода

    await state.update_data(cost=cost_text)
    keyboard = get_format_keyboard()
    await message.answer(
        f"✅ Выбрана стоимость: {cost_text}\n\nТеперь выберите формат мероприятия:",
        reply_markup=keyboard
    )
    await state.set_state(FilterStates.format)


@router.callback_query(FilterStates.cost, F.data.startswith("cost:"))
async def filter_cost(callback: types.CallbackQuery, state: FSMContext):
    """Обрабатывает выбор стоимости из предложенных вариантов"""
    cost = callback.data.split(":")[1]
    await state.update_data(cost=cost)
    keyboard = get_format_keyboard()
    await callback.message.edit_text(
        f"✅ Выбрана стоимость: {cost}\n\nТеперь выберите формат мероприятия:",
        reply_markup=keyboard
    )
    await state.set_state(FilterStates.format)


def validate_cost_format(text: str) -> bool:
    """
    Проверяет, соответствует ли введённая пользователем стоимость корректному формату.
    Возможные варианты:
    - Числовой диапазон: "10000-20000"
    - Фраза с "от": "От 10000 до 20000"
    - Фраза с "до": "До 20000"
    """
    text = text.lower()

    pattern_range = r"^\d{1,6}-\d{1,6}$"  # 10000-20000
    pattern_from_to = r"^от \d{1,6} до \d{1,6}$"  # От 10000 до 20000
    pattern_to = r"^до \d{1,6}$"  # До 20000

    return bool(re.match(pattern_range, text) or re.match(pattern_from_to, text) or re.match(pattern_to, text))


# @router.callback_query(FilterStates.cost, F.data.startswith("cost:"))
# async def filter_cost(callback: types.CallbackQuery, state: FSMContext):
#     cost = callback.data.split(":")[1]
#     await state.update_data(cost=cost)
#     keyboard = get_format_keyboard()
#     await callback.message.edit_text(
#         f"Выбрана стоимость: {cost}\n\nВыберите формат мероприятия:",
#         reply_markup=keyboard
#     )
#     await state.set_state(FilterStates.format)


def register_cost_handlers(dp):
    dp.include_router(router)
