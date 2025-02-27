import sqlite3


class Database:
    def __init__(self, db_path: str = "bot_database.sqlite"):
        """Инициализация БД и создание таблиц, если их нет"""
        self.db_path = db_path
        self._create_tables()

    def _connect(self):
        """Создаёт подключение к БД"""
        return sqlite3.connect(self.db_path)

    def _create_tables(self):
        """Создаёт таблицы, если их нет"""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_filters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                subscription_name TEXT NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                cost TEXT NOT NULL,
                format TEXT NOT NULL,
                location TEXT NOT NULL
            )
        """)

        # Создаем таблицу настроек уведомлений
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_notification_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            notification_period TEXT NOT NULL,
            UNIQUE(user_id, notification_period)
        )
        ''')

        cursor.execute("""
                        CREATE TABLE IF NOT EXISTS events (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            event_date TEXT NOT NULL,
                            event_name TEXT NOT NULL,
                            description TEXT,
                            location TEXT,
                            event_type TEXT NOT NULL,
                            event_link TEXT,
                            category TEXT,
                            hashtags TEXT,
                            cost TEXT,
                            event_time TEXT,
                            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)

        conn.commit()
        conn.close()

    def get_connection(self):
        """Возвращает подключение к БД"""
        return self._connect()

    def update_events(self, events_data: list[dict]):
        """Обновление событий с использованием контекстного менеджера."""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM events")
            for event in events_data:
                cursor.execute("""
                    INSERT INTO events (event_date, event_name, description, location, 
                                      event_type, event_link, category, hashtags, cost, event_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.get("Дата"),
                    event.get("Наименование мероприятия"),
                    event.get("Краткое описание"),
                    event.get("Место расположения"),
                    event.get("Тип мероприятия(Офлайн или онлайн)"),
                    event.get("Ссылка на мероприятие"),
                    event.get("Тип основной"),
                    event.get("Хештеги"),
                    event.get("Стоимость"),
                    event.get("Время")
                ))
            conn.commit()
        conn.close()

    def get_all_events(self) -> list[dict]:
        """Получает все мероприятия из БД"""
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT event_date, event_name, description, location, event_type, event_link, category, hashtags
            FROM events
            ORDER BY event_date ASC
        """)

        rows = cursor.fetchall()
        conn.close()

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
