from aiogram import types
from aiogram.exceptions import TelegramBadRequest
from bot.db.queries import get_user_subscriptions
from bot.keyboards.inline_keyboards import get_subscriptions_keyboard, get_main_menu_keyboard

async def show_user_subscriptions(callback_or_message: types.Message | types.CallbackQuery):
    """Отображает список подписок пользователя с кнопками 'Удалить' и 'Поиск мероприятий'"""
    user_id = callback_or_message.from_user.id
    subscriptions = get_user_subscriptions(user_id)

    if not subscriptions:
        text = "😕 У вас пока нет подписок. Добавьте подписку для получения уведомлений."
        keyboard = get_main_menu_keyboard()
    else:
        text = "📜 Ваши подписки:\nВыберите действие:"
        keyboard = get_subscriptions_keyboard(subscriptions)

    if isinstance(callback_or_message, types.CallbackQuery):
        try:
            await callback_or_message.message.edit_text(text, reply_markup=keyboard)
        except TelegramBadRequest as e:
            if "message is not modified" in str(e):
                await callback_or_message.answer("Список подписок не изменился", show_alert=True)
            else:
                raise
        await callback_or_message.answer()
    else:
        await callback_or_message.answer(text, reply_markup=keyboard)