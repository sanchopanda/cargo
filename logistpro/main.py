import os
import requests
import json
from cookie_manager import load_cookies, save_cookies 
from auth import login_and_save_cookies
from datetime import datetime
import re
import logging

# Настройка логирования (можно разместить в начале файла)
logging.basicConfig(level=logging.WARNING)

# Путь к файлу для хранения обработанных ID заявок
PROCESSED_IDS_FILE = 'processed_ids.json'

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

def parse_application(application, processed_ids):
    """Обрабатывает заявку и возвращает структурированные данные.

    Args:
        application (dict): Заявка для обработки.
        processed_ids (set): Набор уже обработанных ID заявок.

    Returns:
        dict or None: Структурированные данные заявки или None, если заявка уже обработана.
    """
    application_id = application.get('Id', 'Не указано')

    # Проверяем, была ли заявка уже обработана
    if application_id in processed_ids:
        logging.info(f"Заявка с ID {application_id} уже обработана. Пропуск.")
        return None  # Или можно вернуть специальный маркер

    transport_summary = application.get('TransportSummary', 'Не указано')
    route = application.get('Route', 'Не указано')
    cargo_parameters = application.get('CargoParameters', 'Не указано')

    # Инициализируем переменные
    cargo_type = "Не указано"
    loading_type = "Не указано"
    waypoints = []

    # Инициализируем списки для хранения данных погрузки и выгрузки
    loading_addresses = []
    loading_dates = []
    loading_time_starts = []
    loading_time_ends = []
    unloading_addresses = []
    unloading_dates = []
    unloading_time_starts = []
    unloading_time_ends = []

    # Словарь для сопоставления CargoType с CargoTypeID
    cargo_type_mapping = {
        "Тент": 200,
        "Рефрижератор": 300,
        "Изотерм": 400,
        "Борт": 1100,
        "Тент/Борт": 200,
        "Трал": 10700,
        "Любой закрытый": 30000,
        "Любой открытый": 20000
    }

    # Словарь для сопоставления LoadingType с LoadingTypeID
    loading_type_mapping = {
        "Задняя": 4,
        "задняя": 4
    }

    # Ищем и выделяем нужные данные из TransportSummary
    if transport_summary != "Не указано":
        cargo_type_start = transport_summary.find("Тип кузова:") + len("Тип кузова:")
        cargo_type_end = transport_summary.find("\n", cargo_type_start)
        cargo_type = transport_summary[cargo_type_start:cargo_type_end].strip()

        loading_type_start = transport_summary.find("Тип погрузки/выгрузки:") + len("Тип погрузки/выгрузки:")
        loading_type_end = transport_summary.find("\n", loading_type_start)
        loading_type = transport_summary[loading_type_start:loading_type_end].strip()

    # Получение CargoTypeID из словаря
    cargo_type_id = cargo_type_mapping.get(cargo_type, "Не указано")

    # Получение LoadingTypeID из словаря
    loading_type_id = loading_type_mapping.get(loading_type, "Не указано")

    # Парсинг маршрута
    if route != "Не указано":
        route_lines = route.split('●')
        for line in route_lines[1:]:  # Пропускаем первую часть до первого '●'
            line = line.strip()
            if not line:
                continue
            try:
                # Разделяем на тип и остальную часть
                type_part, rest = line.split(':', 1)
                # Извлекаем время и адрес
                time_part, address_part = rest.split('\n', 1)
                # Извлекаем время
                time = time_part.strip()
                # Извлекаем адрес после 'Адрес:'
                address = address_part.split(':', 1)[1].strip() if 'Адрес:' in address_part else 'Не указано'

                # Добавляем в список waypoints
                waypoints.append(f"{type_part.strip()} ● {time} ● {address}")
            except ValueError:
                # Если формат строки некорректен, пропускаем
                logging.warning(f"Некорректный формат строки маршрута: {line}")
                continue

    # Разделяем точки маршрута на погрузку и выгрузку
    for waypoint in waypoints:
        parts = waypoint.split(' ● ')
        if len(parts) != 3:
            logging.warning(f"Некорректные записи WayPoints: {waypoint}")
            continue  # Пропускаем некорректные записи
        type_, time_str, address = parts

        # Разделяем время на начало и конец
        if ' - ' in time_str:
            time_start, time_end = time_str.split(' - ', 1)
            time_start = time_start.strip()
            time_end = time_end.strip()
        else:
            time_start = time_str.strip()
            time_end = "Не указано"

        # Извлекаем дату и преобразуем формат
        if ' ' in time_start:
            date_str, start_time = time_start.split(' ', 1)
            try:
                date_obj = datetime.strptime(date_str, '%d.%m.%Y')
                formatted_date = date_obj.strftime('%Y-%m-%d')
            except ValueError:
                formatted_date = "Не указано"
                logging.warning(f"Некорректный формат даты: {date_str}")
            loading_time = start_time.strip()
        else:
            formatted_date = "Не указано"
            loading_time = time_start.strip()

        if 'Погрузка' in type_:
            loading_addresses.append(address)
            loading_dates.append(formatted_date)
            loading_time_starts.append(loading_time)
            loading_time_ends.append(time_end)
        elif 'Выгрузка' in type_:
            unloading_addresses.append(address)
            unloading_dates.append(formatted_date)
            unloading_time_starts.append(loading_time)
            unloading_time_ends.append(time_end)

    # Обработка CargoParameters
    if cargo_parameters != "Не указано":
        # Регулярное выражение для извлечения веса и объема
        # Пример 1: "(опасный груз: ADR 8) 21 т. 86 м³"
        # Пример 2: "11,5 т. 90 м³"
        pattern = r"\)\s*(\d+[.,]?\d*)\s*т\.?\s*(\d+[.,]?\d*)\s*м³|^(\d+[.,]?\d*)\s*т\.?\s*(\d+[.,]?\d*)\s*м³$"
        match = re.search(pattern, cargo_parameters)
        if match:
            if match.group(1) and match.group(2):
                # Совпадение с форматом с скобками
                cargo_weight = match.group(1).replace(',', '.').strip()
                cargo_value = match.group(2).replace(',', '.').strip()
            elif match.group(3) and match.group(4):
                # Совпадение с форматом без скобок
                cargo_weight = match.group(3).replace(',', '.').strip()
                cargo_value = match.group(4).replace(',', '.').strip()
            else:
                cargo_weight = "Не указано"
                cargo_value = "Не указано"
                logging.warning(f"Непредвиденный формат CargoParameters: {cargo_parameters}")
        else:
            # Альтернативный парсинг, если регулярное выражение не сработало
            cargo_parts = cargo_parameters.split(' ')
            if len(cargo_parts) >= 4:
                # Ожидаем формат: "21 т. 86 м³"
                if cargo_parts[1].startswith('т.') and cargo_parts[3].startswith('м³'):
                    cargo_weight = cargo_parts[0].replace(',', '.').strip()
                    cargo_value = cargo_parts[2].replace(',', '.').strip()
                else:
                    cargo_weight = "Не указано"
                    cargo_value = "Не указано"
                    logging.warning(f"Некорректный формат CargoParameters: {cargo_parameters}")
            else:
                cargo_weight = "Не указано"
                cargo_value = "Не указано"
                logging.warning(f"Некорректный формат CargoParameters: {cargo_parameters}")
    else:
        cargo_weight = "Не указано"
        cargo_value = "Не указано"

    parsed_data = {
        'Id': application_id,
        'Number': application.get('Number', 'Не указано'),
        'InitCost': application.get('InitCost', 'Не указано'),
        'ProductType': application.get('Cargo', 'Не указано'),
        'CargoParameters': cargo_parameters,          # Добавляем новый ключ
        'CargoWeight': cargo_weight,                  # Добавляем новый ключ
        'CargoValue': cargo_value,                    # Добавляем новый ключ
        'TransportSummary': transport_summary,
        'CargoType': cargo_type,                      # Добавляем новый ключ
        'CargoTypeID': cargo_type_id,                 # Добавляем новый ключ
        'LoadingType': loading_type,                  # Добавляем новый ключ
        'LoadingTypeID': loading_type_id,             # Добавляем новый ключ
        'Route': route,
        'WayPoints': waypoints,                       # Добавляем новый ключ
        'LoadingAddresses': loading_addresses,        # Добавляем новый ключ
        'LoadingDates': loading_dates,                # Добавляем новый ключ
        'LoadingTimeStarts': loading_time_starts,      # Добавляем новый ключ
        'LoadingTimeEnds': loading_time_ends,          # Добавляем новый ключ
        'UnloadingAddresses': unloading_addresses,    # Добавляем новый ключ
        'UnloadingDates': unloading_dates,            # Добавляем новый ключ
        'UnloadingTimeStarts': unloading_time_starts,  # Добавляем новый ключ
        'UnloadingTimeEnds': unloading_time_ends       # Добавляем новый ключ
    }

    # Добавляем ID заявки в набор обработанных
    processed_ids.add(application_id)
    save_processed_ids(processed_ids)

    return parsed_data

# Путь к файлу с куками
COOKIE_FILE = 'cookies.pkl'

# URL для запроса данных
DATA_URL = "https://lk.logistpro.su/api/public/request?mode=Open&tenderType=Order&public=Show"

# Функция для загрузки кук в сессию
def add_cookies_to_session(session, cookie_file):
    if os.path.exists(cookie_file) and os.path.getsize(cookie_file) > 0:
        # Загружаем куки из файла
        cookies = load_cookies(cookie_file)
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])
        return True
    return False

def get_data_with_cookies():
    session = requests.Session()

    # Пытаемся загрузить куки и сделать запрос
    if add_cookies_to_session(session, COOKIE_FILE):
        response = session.get(DATA_URL)
        # Если запрос успешен, выводим результат
        if response.status_code == 200:
            try:
                data = response.json()  # Попытка распарсить JSON
                #print(type(data))  # Выводим тип данных
                #print(json.dumps(data, indent=4, ensure_ascii=False))  # Выводим данные в формате JSON
            except json.JSONDecodeError:
                print("Ошибка парсинга JSON")
            return data
        elif response.status_code == 403:
            print("Получен статус 403, требуется авторизация...")
        else:
            print(f"Ошибка: {response.status_code}")
            return
    else:
        print("Файл с куками отсутствует или пуст.")

    # Если куки не подходят (403) или их нет, авторизуемся через Selenium
    login_and_save_cookies(COOKIE_FILE)
    # Повторяем запрос с новыми куками
    if add_cookies_to_session(session, COOKIE_FILE):
        response = session.get(DATA_URL)
        if response.status_code == 200:
            data = response.json()  # Повторная попытка распарсить JSON
            return data
        else:
            print(f"Ошибка после авторизации: {response.status_code}")
            return None

# Основная программа
if __name__ == "__main__":
    # Загрузка обработанных ID при запуске скрипта
    processed_ids = load_processed_ids()

    data = get_data_with_cookies()

    if data is not None and 'Items' in data:
        applications_dict = {}

        # Проходим по каждому элементу в 'Items' и передаем его в функцию парсинга
        for application in data['Items']:
            parsed_application = parse_application(application, processed_ids)
            if parsed_application:
                app_id = parsed_application['Id']
                applications_dict[app_id] = parsed_application

        # Выводим итоговый словарь с обработанными заявками
        print(json.dumps(applications_dict, indent=4, ensure_ascii=False))
    else:
        print("Нет данных для обработки.")
