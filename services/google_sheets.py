from gspread import service_account
from typing import List, Dict
from config import SERVICE_ACCOUNT_FILE, GOOGLE_SHEET_ID, SHEET_NAME


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
    headers = worksheet.row_values(1)[:-3]  # Заголовки из первой строки
    rows = worksheet.get_all_values()[1:]  # Данные со второй строки

    # Преобразуем данные в список словарей
    data = []
    for row in rows:
        row_dict = {headers[i]: value for i, value in enumerate(row[:-3])}
        data.append(row_dict)

    return data
