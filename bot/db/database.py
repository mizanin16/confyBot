import sqlite3
from datetime import datetime
from typing import List, Dict

class Database:
    def __init__(self, db_path: str = "bot_database.sqlite"):
        """Инициализация БД и создание таблиц, если их нет"""
        self.db_path = db_path
        self._create_tables()  # Создаём таблицы только если их нет

    def _connect(self):
        """Создаёт подключение к БД"""
        return sqlite3.connect(self.db_path)

    def _create_tables(self):
        """Создаёт таблицы, если их нет, без удаления существующих данных"""
        conn = self._connect()
        cursor = conn.cursor()
        self.clear_events()
        # Таблица user_filters
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_filters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                subscription_name TEXT NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,  -- Оставляем TEXT для хранения диапазонов DD.MM.YYYY - DD.MM.YYYY
                cost TEXT NOT NULL,
                format TEXT NOT NULL,
                location TEXT NOT NULL
            )
        """)

        # Таблица user_notification_settings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_notification_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                notification_period TEXT NOT NULL,
                UNIQUE(user_id, notification_period)
            )
        """)

        # Таблица events с датой в формате YYYY-MM-DD
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_date TEXT NOT NULL CHECK(length(event_date) = 10),  -- Формат YYYY-MM-DD
                event_name TEXT NOT NULL,
                description TEXT,
                location TEXT,
                event_type TEXT NOT NULL,
                event_link TEXT,
                category TEXT,
                hashtags TEXT,
                cost TEXT,  -- Оставляем TEXT для "Бесплатно" или диапазонов
                event_time TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def get_connection(self):
        """Возвращает подключение к БД"""
        return self._connect()

    def update_events(self, events_data: List[Dict[str, str]]):
        with self._connect() as conn:
            self.clear_events()
            cursor = conn.cursor()
            for event in events_data:
                raw_date = event.get("Дата", "")
                # Преобразование даты из Google Sheets (DD.MM.YYYY) в YYYY-MM-DD
                try:
                    if raw_date:
                        event_date = datetime.strptime(raw_date, "%d.%m.%Y").strftime("%Y-%m-%d")
                    else:
                        event_date = datetime.now().strftime("%Y-%m-%d")  # Значение по умолчанию
                except ValueError as e:
                    print(f"Ошибка формата даты: {raw_date}, используется текущая дата. Ошибка: {e}")
                    event_date = datetime.now().strftime("%Y-%m-%d")

                cursor.execute("""
                    INSERT INTO events (event_date, event_name, description, location, 
                                      event_type, event_link, category, hashtags, cost, event_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event_date,
                    event.get("Наименование мероприятия", ""),
                    event.get("Краткое описание"),
                    event.get("Место расположения"),
                    event.get("Тип мероприятия(Офлайн или онлайн)", ""),
                    event.get("Ссылка на мероприятие"),
                    event.get("Тип основной", "").upper(),
                    event.get("Хештеги"),
                    event.get("Стоимость"),
                    event.get("Время")
                ))
            conn.commit()

    def clear_events(self):
        """Очищает таблицу events (вызывается вручную при необходимости)."""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM events")
            conn.commit()

    def get_all_events(self) -> List[Dict[str, str]]:
        """Получает все мероприятия из БД"""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT event_date, event_name, description, location, event_type, event_link, category, hashtags, cost
                FROM events
                ORDER BY event_date ASC
            """)
            rows = cursor.fetchall()

        return [{
            "Дата": row[0],
            "Наименование мероприятия": row[1],
            "Краткое описание": row[2],
            "Место расположения": row[3],
            "Тип мероприятия(Офлайн или онлайн)": row[4],
            "Ссылка на мероприятие": row[5],
            "Тип основной": row[6],
            "Хештеги": row[7],
            "Стоимость": row[8]
        } for row in rows]