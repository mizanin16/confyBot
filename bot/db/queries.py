from .database import Database

db = Database()


def save_filters(user_id: int, subscription_name: str, category: str, date: str, cost: str, format_: str,
                 location: str):
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


def get_filtered_events(filter_details: dict) -> list:
    """
    Получает мероприятия, соответствующие заданным фильтрам

    Args:
        filter_details: Словарь с параметрами фильтров

    Returns:
        list: Список мероприятий, соответствующих фильтрам
    """
    conn = db.get_connection()
    cursor = conn.cursor()

    # Базовый запрос
    query = """
        SELECT id, event_date, event_name, description, location, event_type, 
               event_link, category, hashtags, cost, event_time
        FROM events
        WHERE 1=1
    """
    params = []

    # Фильтрация по категории
    if filter_details.get('category') and filter_details['category'] != "Показать все" and filter_details[
        'category'] != "Не выбрано":
        categories = filter_details['category'].split(', ')
        category_conditions = []

        for category in categories:
            category_conditions.append("category LIKE ?")
            params.append(f"%{category.upper()}%")

        query += f" AND ({' OR '.join(category_conditions)})"

    # Фильтрация по стоимости
    if filter_details.get('cost') and filter_details['cost'] != "Показывать все" and filter_details[
        'cost'] != "Не выбрано":
        if filter_details['cost'] == "Бесплатно":
            query += " AND (cost LIKE ? OR cost = '0' OR cost = '')"
            params.append("%бесплатно%")
        elif "До" in filter_details['cost']:
            try:
                value = ''.join(c for c in filter_details['cost'] if c.isdigit())
                if value:
                    value = int(value)
                    query += " AND (CAST(REPLACE(REPLACE(cost, ' ', ''), '.', '') AS INTEGER) < ? OR cost LIKE ?)"
                    params.extend([value, "%бесплатно%"])
            except (ValueError, TypeError):
                pass
        elif "От" in filter_details['cost']:
            try:
                value = ''.join(c for c in filter_details['cost'] if c.isdigit())
                if value:
                    value = int(value)
                    query += " AND CAST(REPLACE(REPLACE(cost, ' ', ''), '.', '') AS INTEGER) >= ?"
                    params.append(value)
            except (ValueError, TypeError):
                pass

    # Фильтрация по дате
    if filter_details.get('date') and filter_details['date'] != "Не выбрано":
        if " - " in filter_details['date']:
            try:
                start_date, end_date = filter_details['date'].split(" - ")
                query += " AND (strftime('%Y%m%d', substr(event_date, 7, 4) || '-' || substr(event_date, 4, 2) || '-' || substr(event_date, 1, 2)) BETWEEN strftime('%Y%m%d', ?) AND strftime('%Y%m%d', ?))"
                start_parts = start_date.split('.')
                end_parts = end_date.split('.')
                start_formatted = f"{start_parts[2]}-{start_parts[1]}-{start_parts[0]}"
                end_formatted = f"{end_parts[2]}-{end_parts[1]}-{end_parts[0]}"
                params.extend([start_formatted, end_formatted])
            except (ValueError, IndexError):
                pass
        else:
            try:
                date_parts = filter_details['date'].split('.')
                date_formatted = f"{date_parts[2]}-{date_parts[1]}-{date_parts[0]}"
                query += " AND strftime('%Y%m%d', substr(event_date, 7, 4) || '-' || substr(event_date, 4, 2) || '-' || substr(event_date, 1, 2)) = strftime('%Y%m%d', ?)"
                params.append(date_formatted)
            except (ValueError, IndexError):
                pass

    # Сортировка по дате
    query += " ORDER BY strftime('%Y%m%d', substr(event_date, 7, 4) || '-' || substr(event_date, 4, 2) || '-' || substr(event_date, 1, 2)) ASC"

    print(query, params)  # Для отладки
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [{
        "id": row[0],
        "event_date": row[1],
        "event_name": row[2],
        "description": row[3],
        "location": row[4],
        "event_type": row[5],
        "event_link": row[6],
        "category": row[7],
        "hashtags": row[8],
        "cost": row[9],
        "event_time": row[10]
    } for row in rows]


def get_filter_by_name(user_id: int, subscription_name: str):
    """
    Получает детали фильтра по имени подписки для конкретного пользователя

    Args:
        user_id: ID пользователя
        subscription_name: Название подписки

    Returns:
        dict: Словарь с параметрами фильтра или None, если фильтр не найден
    """
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, subscription_name, category, date, cost, format, location 
        FROM user_filters
        WHERE user_id = ? AND subscription_name = ?
        ORDER BY id DESC
        LIMIT 1
    """, (user_id, subscription_name))

    result = cursor.fetchone()
    conn.close()

    if result:
        return {
            "subscription_name": result[1],
            "category": result[2],
            "date": result[3],
            "cost": result[4],
            "format": result[5],
            "location": result[6]
        }
    return None
