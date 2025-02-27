from aiogram import Router, types, F
from bot.keyboards.inline_keyboards import get_main_menu_keyboard
from handlers.subscriptions.utils import show_user_subscriptions

router = Router()

@router.callback_query(F.data == "view_subscriptions")
async def view_subscriptions(callback: types.CallbackQuery):
    """Обработчик кнопки 'Мои подписки'"""
    await show_user_subscriptions(callback)

@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    """Возвращает пользователя в главное меню"""
    await callback.message.edit_text("👋 Добро пожаловать в главное меню!", reply_markup=get_main_menu_keyboard())
    await callback.answer()
