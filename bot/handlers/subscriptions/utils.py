from aiogram import types, exceptions
from bot.db.queries import get_user_subscriptions
from bot.keyboards.inline_keyboards import get_subscriptions_keyboard, get_main_menu_keyboard
from aiogram.exceptions import TelegramBadRequest


async def show_user_subscriptions(callback_or_message: types.Message | types.CallbackQuery):
    """Отображает список подписок пользователя (универсальная функция)"""
    user_id = callback_or_message.from_user.id
    subscriptions = get_user_subscriptions(user_id)

    if not subscriptions:
        text = "😕 У вас пока нет подписок. Добавьте подписку для получения уведомлений."
        keyboard = get_main_menu_keyboard()

        # Показываем сообщение и завершаем обработку
        if isinstance(callback_or_message, types.CallbackQuery):
            try:
                await callback_or_message.message.edit_text(text, reply_markup=keyboard)
            except TelegramBadRequest as e:
                if "message is not modified" in str(e):
                    # Если содержимое одинаковое, показываем информационное всплывающее сообщение
                    await callback_or_message.answer("У вас нет активных подписок", show_alert=True)
                else:
                    raise
            await callback_or_message.answer()
        else:
            await callback_or_message.answer(text, reply_markup=keyboard)
        return  # Завершаем функцию, дальше ничего не делаем

    # Код для обработки наличия подписок (выполняется только если есть подписки)
    text = "📜 Ваши подписки:\nВыберите для удаления:"
    keyboard = get_subscriptions_keyboard(subscriptions)

    if isinstance(callback_or_message, types.CallbackQuery):
        try:
            await callback_or_message.message.edit_text(text, reply_markup=keyboard)
        except TelegramBadRequest as e:
            if "message is not modified" in str(e):
                pass
            else:
                raise
        await callback_or_message.answer()
    else:
        await callback_or_message.answer(text, reply_markup=keyboard)