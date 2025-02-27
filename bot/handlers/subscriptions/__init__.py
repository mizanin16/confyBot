from aiogram import Router

from .view import router as view_router
from .delete import router as delete_router

# Создаём общий роутер
router = Router()

# Добавляем все подроутеры
router.include_router(view_router)
router.include_router(delete_router)


# Функция для подключения всех фильтров
def register_subscription_handlers(dp):
    dp.include_router(router)
