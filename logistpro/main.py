import os
import json
import logging
import time  # Добавлен импорт модуля time
from dotenv import load_dotenv
from config import (
    COOKIE_FILE,
    AUTHORIZATION_TOKEN
)
from session_manager import get_data_with_cookies
from application_processor import process_applications
from auth import login_and_save_cookies  # Импорт функции авторизации

def main():
    """Основная функция программы."""
    # Настройка логирования
    logging.basicConfig(level=logging.DEBUG)  # Установлен уровень DEBUG для отображения всех сообщений

    while True:  # Добавлен бесконечный цикл
        try:
            # Проверка существования файла куки
            if not os.path.exists(COOKIE_FILE) or os.path.getsize(COOKIE_FILE) == 0:
                logging.info("Файл куки пустой или не существует. Запуск процесса авторизации через Selenium.")
                login_and_save_cookies(COOKIE_FILE)

            # Получаем данные с использованием куки
            data = get_data_with_cookies(COOKIE_FILE)

            if data is not None and 'Items' in data:
                applications_dict, request_bodies = process_applications(data, AUTHORIZATION_TOKEN)

                # Запись всех тел запросов в JSON-файл
                with open('request_bodies.json', 'w', encoding='utf-8') as f:
                    json.dump(request_bodies, f, ensure_ascii=False, indent=4)
                    logging.info("Все тела запросов записаны в request_bodies.json")
            else:
                logging.info("Нет данных для обработки.")

        except Exception as e:
            logging.exception(f"Произошла ошибка: {e}")

        logging.info("Ожидание 5 минут перед следующей проверкой...")
        time.sleep(300)  # Пауза в 5 минут перед повторной проверкой

if __name__ == "__main__":
    main()