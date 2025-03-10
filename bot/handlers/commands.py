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
    await message.answer("🤔 Как я могу помочь вам?\n\n"
                         "Я помогу вам отследить предстоящие мероприятия.\n\n"
                         "1️⃣ /start - запустить бота и выбрать категорию\n"
                         "2️⃣ /subscriptions - получить сведения о добавленных подписках\n"
                         "3️⃣ /settings - настройки бота\n\n"
                         "Если у вас возникли вопросы или вы хотите оставить отзыв, "
                         "напишите мне @mizanin16\n\n"
                         "Спасибо за ваше внимание! 😊"
                         )


@router.message(Command("commands"))
async def commands_command(message: types.Message):
    await message.answer("Список команд:\n"
                         "1️⃣ /start - запустить бота и выбрать категорию\n"
                         "2️⃣ /subscriptions - получить сведения о добавленных подписках\n"
                         "3️⃣ /settings - настройки бота\n\n")


def register_command_handlers(dp):
    dp.include_router(router)
