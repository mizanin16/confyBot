from .database import Database

db = Database()


def save_filters(user_id: int, subscription_name: str, category: str, date: str, cost: str, format_: str, location: str):
    """Сохраняет выбранные пользователем фильтры в БД"""
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_filters (user_id, subscription_name, category, date, cost, format, location)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, subscription_name, category, date, cost, format_, location))
    conn.commit()
    conn.close()


def get_user_filters(user_id: int):
    """Получает последние сохранённые фильтры пользователя"""
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT subscription_name,category, date, cost, format, location FROM user_filters
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 1
    """, (user_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return {
            "subscription_name": result[0],
            "category": result[1],
            "date": result[2],
            "cost": result[3],
            "format": result[4],
            "location": result[5]
        }
    return None


def get_user_subscriptions(user_id: int):
    """Получает список подписок пользователя"""
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, subscription_name FROM user_filters
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,))
    result = cursor.fetchall()
    conn.close()
    return result  # Список кортежей (id, subscription_name)


def delete_subscription(subscription_id: int):
    """Удаляет подписку по ID"""
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM user_filters WHERE id = ?
    """, (subscription_id,))
    conn.commit()
    conn.close()


def create_notification_settings_table():
    """Создает таблицу для хранения настроек уведомлений пользователей"""
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_notification_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        notification_period TEXT NOT NULL,
        UNIQUE(user_id, notification_period)
    )
    ''')
    conn.commit()
    conn.close()


def save_user_notification_settings(user_id: int, notification_periods: list):
    """
    Сохраняет настройки уведомлений пользователя

    Args:
        user_id: ID пользователя
        notification_periods: Список периодов уведомлений (например, ['30d', '7d', '1d'])
    """
    conn = db.get_connection()
    cursor = conn.cursor()

    # Удаляем текущие настройки пользователя
    cursor.execute("DELETE FROM user_notification_settings WHERE user_id = ?", (user_id,))

    # Добавляем новые настройки
    for period in notification_periods:
        cursor.execute(
            "INSERT INTO user_notification_settings (user_id, notification_period) VALUES (?, ?)",
            (user_id, period)
        )

    conn.commit()
    conn.close()


def get_user_notification_settings(user_id: int) -> list:
    """
    Получает настройки уведомлений пользователя

    Args:
        user_id: ID пользователя

    Returns:
        list: Список периодов уведомлений (например, ['30d', '7d', '1d'])
    """
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT notification_period FROM user_notification_settings WHERE user_id = ?",
        (user_id,)
    )

    results = cursor.fetchall()
    conn.close()

    # Преобразуем результаты в список
    return [row[0] for row in results]


def get_users_for_notification(days_before: str) -> list:
    """
    Получает список пользователей, которые выбрали определенный период уведомлений

    Args:
        days_before: Период уведомления (например, '30d', '7d', '1d')

    Returns:
        list: Список ID пользователей
    """
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT DISTINCT user_id FROM user_notification_settings WHERE notification_period = ?",
        (days_before,)
    )

    results = cursor.fetchall()
    conn.close()

    # Преобразуем результаты в список ID пользователей
    return [row[0] for row in results]

def get_filter_details(subscription_id: int):
    """

    Получает детали фильтра по ID подписки
    """
    conn = db.get_connection()
    cursor = conn.cursor()
    print(subscription_id)
    cursor.execute("""
        SELECT subscription_name,category, date, cost, format, location FROM user_filters
        WHERE id = ?
    """, (subscription_id,))

    result = cursor.fetchone()
    conn.close()

    if result:
        return {
            "subscription_name": result[0],
            "category": result[1],
            "date": result[2],
            "cost": result[3],
            "format": result[4],
            "location": result[5]
        }
    return None

