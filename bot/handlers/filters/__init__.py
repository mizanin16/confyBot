from aiogram import Router

from .date_handlers import router as date_router
from .cost_handlers import router as cost_router
from .location_handlers import router as location_router
from .format_handlers import router as format_router
from .category_handlers import router as category_router


# Создаём общий роутер
filters_router = Router()

# Добавляем все подроутеры
filters_router.include_router(category_router)
filters_router.include_router(location_router)
filters_router.include_router(date_router)
filters_router.include_router(cost_router)
filters_router.include_router(format_router)

# Функция для подключения всех фильтров
def register_filter_handlers(dp):
    dp.include_router(filters_router)
