from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.db.queries import save_user_notification_settings, get_user_notification_settings

router = Router()


@router.callback_query(F.data == "settings")
async def settings_menu(callback: types.CallbackQuery):
    """Обработчик кнопки 'Настройки'"""
    keyboard = get_settings_keyboard()
    await callback.message.edit_text("⚙️ Меню настроек", reply_markup=keyboard)
    await callback.answer()

@router.message(Command("settings"))
async def settings_menu_message(message: types.Message):
    """Обработчик команды /settings для Message"""
    keyboard = get_settings_keyboard()
    await message.answer("⚙️ Меню настроек", reply_markup=keyboard)


@router.callback_query(F.data == "notification_settings")
async def notification_settings(callback: types.CallbackQuery):
    """Обработчик кнопки настройки уведомлений"""
    user_id = callback.from_user.id
    # Получаем текущие настройки пользователя
    current_settings = get_user_notification_settings(user_id)

    keyboard = get_notification_settings_keyboard(current_settings)
    await callback.message.edit_text(
        "🔔 Настройка уведомлений\n\n"
        "Выберите, за какое время до мероприятия вы хотите получать уведомления:",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data.startswith("toggle_notification_"))
async def toggle_notification(callback: types.CallbackQuery):
    """Обработчик переключения настроек уведомлений"""
    user_id = callback.from_user.id
    period = callback.data.split("_")[2]  # Извлекаем период из callback_data

    # Получаем текущие настройки
    current_settings = get_user_notification_settings(user_id)

    # Инвертируем настройку для выбранного периода
    if period in current_settings:
        current_settings.remove(period)
    else:
        current_settings.append(period)

    # Сохраняем обновленные настройки
    save_user_notification_settings(user_id, current_settings)

    # Обновляем клавиатуру с новыми настройками
    keyboard = get_notification_settings_keyboard(current_settings)
    await callback.message.edit_text(
        "🔔 Настройка уведомлений\n\n"
        "Выберите, за какое время до мероприятия вы хотите получать уведомления:",
        reply_markup=keyboard
    )
    await callback.answer("Настройки уведомлений обновлены")


@router.callback_query(F.data == "save_notification_settings")
async def save_notification_settings(callback: types.CallbackQuery):
    """Обработчик сохранения настроек и возврата в меню настроек"""
    await settings_menu(callback)
    await callback.answer("Настройки уведомлений сохранены!")


@router.callback_query(F.data == "back_to_main_from_settings")
async def back_to_main_from_settings(callback: types.CallbackQuery):
    """Возврат в главное меню из настроек"""
    from keyboards.inline_keyboards import get_main_menu_keyboard

    await callback.message.edit_text("👋 Добро пожаловать в главное меню!", reply_markup=get_main_menu_keyboard())
    await callback.answer()


def get_settings_keyboard():
    """Клавиатура меню настроек"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔔 Настройка уведомлений", callback_data="notification_settings")],
        [InlineKeyboardButton(text="⬅️ Вернуться в главное меню", callback_data="back_to_main")]
    ])
    return keyboard


def get_notification_settings_keyboard(current_settings):
    """Создает клавиатуру для настройки уведомлений с текущими выбранными опциями"""
    builder = InlineKeyboardBuilder()

    # Определяем доступные периоды уведомлений и их описания
    notification_periods = {
        "30d": "За 30 дней",
        "14d": "За 2 недели",
        "7d": "За 1 неделю",
        "3d": "За 3 дня",
        "1d": "За 1 день"
    }

    # Добавляем кнопки с отметками о выбранных периодах
    for period_id, period_name in notification_periods.items():
        if period_id in current_settings:
            # Выбранный период отмечаем галочкой
            button_text = f"✅ {period_name}"
        else:
            # Невыбранный период без отметки
            button_text = f"⬜ {period_name}"

        builder.add(InlineKeyboardButton(
            text=button_text,
            callback_data=f"toggle_notification_{period_id}"
        ))

    # Располагаем кнопки в столбик
    builder.adjust(1)

    # Добавляем кнопки сохранения и возврата
    builder.row(
        InlineKeyboardButton(text="💾 Сохранить", callback_data="save_notification_settings"),
        InlineKeyboardButton(text="⬅️ Назад", callback_data="settings")
    )

    return builder.as_markup()


def register_settings_handlers(dp):
    dp.include_router(router)
