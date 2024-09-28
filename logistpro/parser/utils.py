import logging
from datetime import datetime

def convert_date(date_str):
    """Преобразует дату из формата 'dd.mm.yyyy' в 'yyyy-mm-dd'."""
    try:
        date_obj = datetime.strptime(date_str, '%d.%m.%Y')
        return date_obj.strftime('%Y-%m-%d')
    except ValueError:
        logging.warning(f"Некорректный формат даты: {date_str}")
        return "Не указано"