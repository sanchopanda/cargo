import os
import requests
import json
import logging
from datetime import datetime
import re
from dotenv import load_dotenv
from cookie_manager import load_cookies
from auth import login_and_save_cookies
from data_manager import load_processed_ids
from parser import parse_application
from request_builder import create_request_body
from config import (
    COOKIE_FILE,
    DATA_URL,
    AUTHORIZATION_TOKEN,
    MAIN_URL
)

from requests import Session

def add_cookies_to_session(session, cookie_file):
    """Загружает куки из файла и добавляет их в сессию.

    Args:
        session (Session): Объект сессии Requests.
        cookie_file (str): Путь к файлу с куками.

    Returns:
        bool: True, если куки успешно загружены и добавлены, иначе False.
    """
    if os.path.exists(cookie_file) and os.path.getsize(cookie_file) > 0:
        # Загружаем куки из файла
        cookies = load_cookies(cookie_file)
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])
        return True
    return False

def get_data_with_cookies():
    """Получает данные с использованием кук.

    Returns:
        dict или None: Полученные данные или None в случае ошибки.
    """
    session = requests.Session()

    # Пытаемся загрузить куки и сделать запрос
    if add_cookies_to_session(session, COOKIE_FILE):
        response = session.get(DATA_URL)
        # Если запрос успешен, выводим результат
        if response.status_code == 200:
            try:
                data = response.json()  # Попытка распарсить JSON
            except json.JSONDecodeError:
                print("Ошибка парсинга JSON")
                return None
            return data
        elif response.status_code == 403:
            print("Получен статус 403, требуется авторизация...")
        else:
            print(f"Ошибка: {response.status_code}")
            return None
    else:
        print("Файл с куками отсутствует или пуст.")

    # Если куки не подходят (403) или их нет, авторизуемся через Selenium
    login_and_save_cookies(COOKIE_FILE)
    # Повторяем запрос с новыми куками
    if add_cookies_to_session(session, COOKIE_FILE):
        response = session.get(DATA_URL)
        if response.status_code == 200:
            try:
                data = response.json()  # Повторная попытка распарсить JSON
                return data
            except json.JSONDecodeError:
                print("Ошибка парсинга JSON после авторизации")
                return None
        else:
            print(f"Ошибка после авторизации: {response.status_code}")
            return None
    else:
        print("Не удалось загрузить новые куки после авторизации.")
        return None

def main():
    """Основная функция программы."""
    # Настройка логирования
    logging.basicConfig(level=logging.DEBUG)  # Установлен уровень DEBUG для отображения всех сообщений

    # Загрузка обработанных ID при запуске скрипта
    processed_ids = load_processed_ids()

    data = get_data_with_cookies()

    if data is not None and 'Items' in data:
        applications_dict = {}
        request_bodies = {}  # Словарь для хранения тел запросов

        for application in data['Items']:
            parsed_application = parse_application(application, processed_ids, AUTHORIZATION_TOKEN)
            if parsed_application:
                app_id = parsed_application['Id']
                applications_dict[app_id] = parsed_application

                # Создаем тело запроса
                request_body = create_request_body(parsed_application)
                request_bodies[app_id] = request_body

                # Выводим тело запроса для проверки
                logging.debug(f"Тело запроса для заявки {app_id}: {json.dumps(request_body, ensure_ascii=False, indent=4)}")
                print(f"Тело запроса для заявки {app_id}:")
                print(json.dumps(request_body, ensure_ascii=False, indent=4))

        logging.info(f"Все распарсенные заявки: {json.dumps(applications_dict, indent=4, ensure_ascii=False)}")
        print(json.dumps(applications_dict, indent=4, ensure_ascii=False))
    else:
        print("Нет данных для обработки.")

if __name__ == "__main__":
    main()