from typing import List, Dict, Any
from datetime import datetime
from bot.db.queries import Database
import logging

logger = logging.getLogger(__name__)

class EventService:
    def __init__(self, db: Database):
        self.db = db

    def find_events_by_filter(self, subscription_name: str, category: str, date: str,
                              cost: str, format: str, location: str) -> List[Dict[str, Any]]:
        """Поиск мероприятий в БД по заданным фильтрам."""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT event_date, event_name, description, location, event_type, event_link, category, hashtags, cost
            FROM events
            WHERE 1=1
        """
        params = []

        # Фильтр по категории
        if category and category != "Не выбрано" and category != "Показать все":
            categories = [cat.strip() for cat in category.split(", ")]
            query += " AND category IN (" + ",".join("?" for _ in categories) + ")"
            params.extend(categories)

        # Фильтр по дате (теперь даты в формате YYYY-MM-DD)
        if date and date != "Не выбрано":
            if " - " in date:
                start_date_str, end_date_str = date.split(" - ")
                start_date = datetime.strptime(start_date_str, "%d.%m.%Y").strftime("%Y-%m-%d")
                end_date = datetime.strptime(end_date_str, "%d.%m.%Y").strftime("%Y-%m-%d")
                query += " AND event_date BETWEEN ? AND ?"
                params.extend([start_date, end_date])
            else:
                event_date = datetime.strptime(date, "%d.%m.%Y").strftime("%Y-%m-%d")
                query += " AND event_date = ?"
                params.append(event_date)

        # Фильтр по стоимости
        if cost and cost != "Показывать все" and cost != "Не выбрано":
            if cost == "Бесплатно":
                query += " AND (cost = ? OR cost IS NULL)"
                params.append("Бесплатно")
            elif "До" in cost:
                try:
                    max_cost = int(cost.split(" ")[1].replace(".", "").replace("рублей", ""))
                    query += " AND CAST(cost AS INTEGER) <= ?"
                    params.append(max_cost)
                except ValueError:
                    logger.warning(f"Invalid cost format: {cost}")
            elif "От" in cost:
                try:
                    min_cost = int(cost.split(" ")[1].replace(".", "").replace("рублей", ""))
                    query += " AND CAST(cost AS INTEGER) >= ?"
                    params.append(min_cost)
                except ValueError:
                    logger.warning(f"Invalid cost format: {cost}")
            elif "-" in cost:
                try:
                    min_cost, max_cost = map(int, cost.split("-"))
                    query += " AND CAST(cost AS INTEGER) BETWEEN ? AND ?"
                    params.extend([min_cost, max_cost])
                except ValueError:
                    logger.warning(f"Invalid cost range format: {cost}")

        # Фильтр по формату
        if format and format != "Показывать все" and format != "Не выбрано":
            event_type = "Офлайн" if "офлайн" in format.lower() else "Онлайн"
            query += " AND event_type = ?"
            params.append(event_type)

        # Фильтр по местоположению
        if location and location != "Показывать все" and location != "Не выбрано":
            query += " AND location LIKE ?"
            params.append(f"%{location}%")

        query += " ORDER BY event_date ASC"

        try:
            logger.info(f"Executing query: {query} with params {params}")
            cursor.execute(query, params)
            rows = cursor.fetchall()
            events = [{
                "id": f"event_{i}",
                "title": row[1],
                "date": row[0],
                "time": "Не указано",
                "cost": row[8] or "Не указано",
                "format": row[4],
                "location": row[3] or "Не указано",
                "description": row[2] or "Описание отсутствует",
                "url": row[5] or "Нет ссылки",
                "category": row[6]
            } for i, row in enumerate(rows)]
            return events
        except Exception as e:
            logger.error(f"Error searching events: {e}")
            return []
        finally:
            conn.close()


    def get_event_details(self, event_id: str) -> Dict[str, Any]:
        """Получение детальной информации о мероприятии по ID."""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT event_date, event_name, description, location, event_type, event_link, category, hashtags, cost
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
                    "cost": row[8] or "Не указано",
                    "format": row[4],
                    "location": row[3] or "Не указано",
                    "description": row[2] or "Подробное описание отсутствует",
                    "url": row[5] or "Нет ссылки",
                    "category": row[6]
                }
            return {}
        except Exception as e:
            print(f"Ошибка при получении деталей мероприятия: {e}")
            return {}
        finally:
            conn.close()