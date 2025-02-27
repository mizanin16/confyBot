import asyncio
from datetime import datetime, timedelta
from aiogram import Bot
from bot.db.queries import get_users_for_notification, get_user_subscriptions, get_filter_details
from bot.services.event_service import EventService


async def send_notification(bot: Bot, user_id: int, message: str):
    """Отправляет уведомление пользователю с обработкой ошибок."""
    try:
        await bot.send_message(user_id, message)
        return True
    except Exception as e:
        print(f"Ошибка при отправке уведомления пользователю {user_id}: {e}")
        return False


async def process_notifications(bot: Bot, event_service: EventService, days_before: int, period_code: str):
    """Обрабатывает уведомления с оптимизацией."""
    users = get_users_for_notification(period_code)
    target_date = (datetime.now() + timedelta(days=days_before)).strftime("%Y-%m-%d")
    sent_notifications = set()  # Для предотвращения дубликатов

    tasks = []
    for user_id in users:
        subscriptions = get_user_subscriptions(user_id)
        if not subscriptions:
            continue

        for sub_id, sub_name in subscriptions:
            filter_details = get_filter_details(sub_id)
            if not filter_details:
                continue

            filter_details['date'] = target_date
            events = event_service.find_events_by_filter(**filter_details)

            if events and (user_id, sub_id) not in sent_notifications:
                message = f"🔔 Напоминание о мероприятиях по подписке '{sub_name}':\n\n"
                for i, event in enumerate(events[:5], 1):
                    message += (f"{i}. {event['title']}\n"
                                f"📅 {event['date']}\n"
                                f"📍 {event['location']}\n\n")

                if len(events) > 5:
                    message += f"...и еще {len(events) - 5} мероприятий\n"
                message += f"Через {days_before} дней."

                tasks.append(send_notification(bot, user_id, message))
                sent_notifications.add((user_id, sub_id))

    # Асинхронная отправка уведомлений
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)


async def schedule_notifications(bot: Bot, event_service: EventService):
    """Гибкое планирование уведомлений."""
    periods = [(30, "30d"), (14, "14d"), (7, "7d"), (3, "3d"), (1, "1d")]

    while True:
        now = datetime.now()
        # Более гибкое время отправки (например, с 9 до 11 утра)
        if 20 <= now.hour <= 21:
            for days, period in periods:
                await process_notifications(bot, event_service, days, period)
            # Спим до следующего дня
            await asyncio.sleep(24 * 3600 - now.hour * 3600 - now.minute * 60)
        else:
            await asyncio.sleep(300)  # Проверка каждые 5 минут