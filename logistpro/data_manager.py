import os
import json
import logging
from config import PROCESSED_IDS_FILE

def load_processed_ids():
    """Загружает список обработанных ID заявок из файла."""
    if os.path.exists(PROCESSED_IDS_FILE):
        try:
            with open(PROCESSED_IDS_FILE, 'r', encoding='utf-8') as file:
                return set(json.load(file))
        except (json.JSONDecodeError, IOError) as e:
            logging.warning(f"Не удалось загрузить файл {PROCESSED_IDS_FILE}: {e}")
            return set()
    else:
        return set()

def save_processed_ids(processed_ids):
    """Сохраняет список обработанных ID заявок в файл."""
    try:
        with open(PROCESSED_IDS_FILE, 'w', encoding='utf-8') as file:
            json.dump(list(processed_ids), file, ensure_ascii=False, indent=4)
    except IOError as e:
        logging.error(f"Не удалось сохранить файл {PROCESSED_IDS_FILE}: {e}")