# bot/states/filter_states.py
from aiogram.fsm.state import State, StatesGroup


class FilterStates(StatesGroup):
    question = State()
    theme = State()
    theme_custom = State()
    geo = State()
    geo_custom = State()
    date = State()
    date_custom = State()
    date_range_start = State()
    date_range_end = State()
    cost = State()
    cost_custom = State()
    format = State()
    format_custom = State()
    confirm = State()
    confirm_selection = State()



class SettingsStates(StatesGroup):
    custom_interval = State()
