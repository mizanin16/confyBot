from aiogram import Router

from bot.handlers.subscriptions.view import router as view_router
from bot.handlers.subscriptions.delete import router as delete_router
from bot.handlers.subscriptions.handlers import router as handlers_router

# Создаём общий роутер
router = Router()

# Добавляем все подроутеры
router.include_router(view_router)
router.include_router(delete_router)
router.include_router(handlers_router)


# Функция для подключения всех фильтров
def register_subscription_handlers(dp):
    dp.include_router(router)
