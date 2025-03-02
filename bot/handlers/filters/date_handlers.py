from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram_calendar.simple_calendar import SimpleCalendar, SimpleCalendarCallback
from datetime import datetime
from bot.states.filter_states import FilterStates
from bot.keyboards.inline_keyboards import get_cost_keyboard
from bot.handlers.filters.common import add_custom_input_button

router = Router()


@router.callback_query(FilterStates.date, F.data == "custom_input")
async def date_custom_input(callback: CallbackQuery, state: FSMContext):
    """Начинает выбор одной даты с календарём"""
    # Создаем календарь без кнопок today и cancel
    calendar = SimpleCalendar()
    calendar.show_today_button = False
    calendar.show_cancel_button = False

    await callback.message.edit_text("📅 Выберите дату:",
                                     reply_markup=await calendar.start_calendar())
    await state.set_state(FilterStates.date_custom)


@router.callback_query(FilterStates.date, F.data == "custom_range_input")
async def date_range_custom_input(callback: CallbackQuery, state: FSMContext):
    """Начинает выбор диапазона дат с календарём"""
    # Создаем календарь без кнопок today и cancel
    calendar = SimpleCalendar()
    calendar.show_today_button = False
    calendar.show_cancel_button = False

    await callback.message.edit_text("📆 Выберите начальную дату:",
                                     reply_markup=await calendar.start_calendar())
    await state.set_state(FilterStates.date_range_start)


@router.callback_query(SimpleCalendarCallback.filter(), FilterStates.date_custom)
@router.callback_query(SimpleCalendarCallback.filter(), FilterStates.date_range_start)
@router.callback_query(SimpleCalendarCallback.filter(), FilterStates.date_range_end)
async def process_calendar_interaction(callback: CallbackQuery, callback_data: SimpleCalendarCallback,
                                       state: FSMContext):
    """Обрабатывает выбор даты, не позволяя выбирать прошедшие даты"""
    # Создаем календарь без кнопок today и cancel
    calendar = SimpleCalendar()
    calendar.show_today_button = False
    calendar.show_cancel_button = False

    selected, date = await calendar.process_selection(callback, callback_data)

    if selected:
        today = datetime.now()

        if date < today:
            await callback.answer("🚫 Нельзя выбрать прошедшую дату! Выберите дату начиная с сегодняшнего дня.",
                                  show_alert=True)
            # ❗ Снова показываем календарь
            await callback.message.edit_text("📅 Выберите дату:",
                                             reply_markup=await calendar.start_calendar())
            return

        if await state.get_state() == FilterStates.date_custom.state:
            selected_date = date.strftime("%d.%m.%Y")
            await state.update_data(date=selected_date)
            await callback.message.edit_text(
                f"✅ Вы выбрали дату: {selected_date}\n\nТеперь выберите стоимость:",
                reply_markup=add_custom_input_button(get_cost_keyboard())
            )
            await state.set_state(FilterStates.cost)

        elif await state.get_state() == FilterStates.date_range_start.state:
            await state.update_data(start_date=date)
            # Для второй даты показываем календарь, начиная с первой выбранной даты
            await callback.message.edit_text("📆 Теперь выберите конечную дату:",
                                             reply_markup=await calendar.start_calendar(year=date.year,
                                                                                        month=date.month))
            await state.set_state(FilterStates.date_range_end)

        elif await state.get_state() == FilterStates.date_range_end.state:
            data = await state.get_data()
            start_date = data.get("start_date")

            if start_date > date:
                await callback.answer("🚫 Конечная дата не может быть раньше начальной! Выберите другую дату.",
                                      show_alert=True)
                # ❗ Снова показываем календарь, начиная с первой выбранной даты
                await callback.message.edit_text("📆 Выберите конечную дату:",
                                                 reply_markup=await calendar.start_calendar(year=start_date.year,
                                                                                            month=start_date.month))
                return

            formatted_range = f"{start_date.strftime('%d.%m.%Y')} - {date.strftime('%d.%m.%Y')}"
            await state.update_data(date=formatted_range)

            await callback.message.edit_text(
                f"✅ Вы выбрали диапазон: {formatted_range}\n\nТеперь выберите стоимость:",
                reply_markup=add_custom_input_button(get_cost_keyboard())
            )
            await state.set_state(FilterStates.cost)