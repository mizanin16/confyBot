from aiogram import Router, types, F
from bot.db.queries import delete_subscription
from bot.handlers.subscriptions.utils import show_user_subscriptions

router = Router()

@router.callback_query(F.data.startswith("delete_sub:"))
async def delete_subscription_handler(callback: types.CallbackQuery):
    """Удаляет подписку и обновляет список"""
    subscription_id = int(callback.data.split(":")[1])
    delete_subscription(subscription_id)

    await callback.answer("✅ Подписка удалена.")
    await show_user_subscriptions(callback)

@router.callback_query(F.data == "back_to_subscriptions")
async def back_to_subscriptions(callback: types.CallbackQuery):
    """Возвращает пользователя к списку подписок"""
    await show_user_subscriptions(callback)
