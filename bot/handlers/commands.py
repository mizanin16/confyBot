from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.handlers.filters.category_handlers import set_filter_name
from bot.keyboards.inline_keyboards import get_main_menu_keyboard

router = Router()

@router.message(Command("start"))
async def start_command(message: types.Message):
    """Приветственное сообщение с меню"""
    await message.answer("👋 Добро пожаловать! Выберите действие:", reply_markup=get_main_menu_keyboard())

@router.callback_query(F.data == "add_subscription")  # Исправлено
async def add_subscription(callback: types.CallbackQuery, state: FSMContext):
    """Запуск добавления подписки"""
    await callback.message.answer(
        "Информация о предстоящих IT-мероприятиях, вебинарах и встречах в пару-тройку кликов!\n\n"
    )
    await set_filter_name(callback.message, state)



@router.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer("Для получения информации о командах используйте /commands")


@router.message(Command("commands"))
async def commands_command(message: types.Message):
    await message.answer("Список команд:\n/start - запустить бота\n/help - справка по боту\n/settings - настройка")



def register_command_handlers(dp):
    dp.include_router(router)

