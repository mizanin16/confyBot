from gspread import service_account
from typing import List, Dict
from bot.config import SERVICE_ACCOUNT_FILE, GOOGLE_SHEET_ID, SHEET_NAME


def connect_to_google_sheets():
    """
    Подключение к Google Sheets через gspread.
    """
    client = service_account(filename=SERVICE_ACCOUNT_FILE)
    table = client.open_by_key(GOOGLE_SHEET_ID)
    return table


def fetch_google_sheet_data() -> List[Dict]:
    """
    Извлекает данные из указанного листа таблицы Google Sheets.

    :return: Список словарей, представляющих данные таблицы.
    """
    table = connect_to_google_sheets()
    worksheet = table.worksheet(SHEET_NAME)
    headers = worksheet.row_values(1)  # Заголовки из первой строки
    rows = worksheet.get_all_values()[1:]  # Данные со второй строки

    # Преобразуем данные в список словарей
    data = []
    for row in rows:
        row_dict = {headers[i]: value for i, value in enumerate(row)}
        data.append(row_dict)

    return data

def append_to_google_sheets(data: Dict):
    """
    Добавляет данные в Google Sheets.

    :param data: Словарь с данными для добавления.
    """
    table = connect_to_google_sheets()
    worksheet = table.worksheet('Users')
    print(data.values())
    values = [str(value) if not isinstance(value, str) else value.strip() for value in data.values()]
    worksheet.append_row(values)