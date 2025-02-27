from typing import List, Dict, Any
import datetime
from bot.db.queries import Database


class EventService:
    def __init__(self, db: Database):
        self.db = db

    def find_events_by_filter(self, subscription_name: str, category: str, date: str,
                              cost: str, format: str, location: str) -> List[Dict[str, Any]]:
        """
        Поиск мероприятий в БД по заданным фильтрам.
        """
        try:
            event_date = datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            event_date = datetime.datetime.now()

        conn = self.db.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT event_date, event_name, description, location, event_type, event_link, category, hashtags
            FROM events
            WHERE 1=1
        """
        params = []

        # Добавляем фильтры в запрос
        if category and category.lower() != "":
            query += " AND category = ?"
            params.append(category)

        query += " AND event_date = ?"
        params.append(event_date.strftime("%Y-%m-%d"))

        if cost != "any":
            query += " AND (cost IS NULL OR cost = ?)"
            params.append("Бесплатно" if cost == "free" else "Платно")

        if format != "any":
            query += " AND event_type = ?"
            params.append("Онлайн" if format == "online" else "Офлайн")

        if location and location.lower() != "any":
            query += " AND location LIKE ?"
            params.append(f"%{location}%")

        query += " ORDER BY event_date ASC"

        try:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            events = [{
                "id": f"event_{i}",
                "title": row[1],
                "date": row[0],
                "time": "Не указано",  # Можно добавить в БД поле времени
                "cost": "Не указано",  # Можно добавить в БД поле стоимости
                "format": row[4],
                "location": row[3] or "Не указано",
                "description": row[2] or "Описание отсутствует",
                "url": row[5]
            } for i, row in enumerate(rows)]

            return events

        except Exception as e:
            print(f"Ошибка при поиске мероприятий: {e}")
            return []
        finally:
            conn.close()

    def get_event_details(self, event_id: str) -> Dict[str, Any]:
        """Получение детальной информации о мероприятии по ID."""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT event_date, event_name, description, location, event_type, event_link, category, hashtags
                FROM events
                WHERE id = ?
            """, (event_id.split('_')[1],))

            row = cursor.fetchone()
            if row:
                return {
                    "id": event_id,
                    "title": row[1],
                    "date": row[0],
                    "time": "Не указано",
                    "cost": "Не указано",
                    "format": row[4],
                    "location": row[3] or "Не указано",
                    "description": row[2] or "Подробное описание отсутствует",
                    "url": row[5],
                    "category": row[6]
                }
            return {}
        except Exception as e:
            print(f"Ошибка при получении деталей мероприятия: {e}")
            return {}
        finally:
            conn.close()