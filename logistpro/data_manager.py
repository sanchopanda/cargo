import json
import logging
import os

from config import PROCESSED_IDS_FILE

def load_processed_ids():
    """Загружает обработанные ID из файла.

    Returns:
        set: Набор обработанных ID.
    """
    if os.path.exists(PROCESSED_IDS_FILE):
        try:
            with open(PROCESSED_IDS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data)
        except json.JSONDecodeError:
            logging.error("Ошибка парсинга JSON в файле обработанных ID.")
            return set()
    else:
        return set()

def save_processed_ids(processed_ids):
    """Сохраняет обработанные ID в файл.

    Args:
        processed_ids (set): Набор обработанных ID.
    """
    try:
        with open(PROCESSED_IDS_FILE, 'w', encoding='utf-8') as f:
            json.dump(list(processed_ids), f, ensure_ascii=False, indent=4)
    except Exception as e:
        logging.error(f"Ошибка при сохранении обработанных ID: {e}")