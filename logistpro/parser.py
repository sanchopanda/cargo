import re
import json
import logging
from datetime import datetime
from api_client import fetch_city_ids
from data_manager import save_processed_ids

def parse_application(application, processed_ids, authorization_token):
    """Обрабатывает заявку и возвращает структурированные данные.

    Args:
        application (dict): Заявка для обработки.
        processed_ids (set): Набор уже обработанных ID заявок.
        authorization_token (str): Токен авторизации для API.

    Returns:
        dict или None: Структурированные данные заявки или None, если заявка уже обработана.
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
        "Задня": 4,
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

    # Получаем уникальные адреса для запроса CityID
    unique_loading_addresses = set(loading_addresses)
    unique_unloading_addresses = set(unloading_addresses)

    logging.info(f"Уникальные адреса погрузки: {unique_loading_addresses}")
    logging.info(f"Уникальные адреса выгрузки: {unique_unloading_addresses}")

    # Получаем CityID для погрузки и выгрузки
    city_ids = fetch_city_ids(unique_loading_addresses, unique_unloading_addresses, authorization_token)

    parsed_data = {
        'Id': application_id,
        'Number': application.get('Number', 'Не указано'),
        'InitCost': application.get('InitCostDec', 'Не указано'),
        'ProductType': application.get('Cargo', 'Не указано'),
        'CargoParameters': cargo_parameters,          # Добавляем новый ключ
        'CargoWeight': cargo_weight,                  # Добавляем новый ключ
        'CargoValue': cargo_value,                    # Добавляем новый ключ
        #'TransportSummary': transport_summary,
        'CargoType': cargo_type,                      # Добавляем новый ключ
        'CargoTypeID': cargo_type_id,                 # Добавляем новый ключ
        'LoadingType': loading_type,                  # Добавляем новый ключ
        'LoadingTypeID': loading_type_id,             # Добавляем новый ключ
        #'Route': route,
        'WayPoints': waypoints,                       # Добавляем новый ключ
        'LoadingAddresses': loading_addresses,        # Добавляем новый ключ
        'LoadingDates': loading_dates,                # Добавляем новый ключ
        'LoadingTimeStarts': loading_time_starts,      # Добавляем новый ключ
        'LoadingTimeEnds': loading_time_ends,          # Добавляем новый ключ
        'UnloadingAddresses': unloading_addresses,    # Добавляем новый ключ
        'UnloadingDates': unloading_dates,            # Добавляем новый ключ
        'UnloadingTimeStarts': unloading_time_starts,  # Добавляем новый ключ
        'UnloadingTimeEnds': unloading_time_ends,      # Добавляем новый ключ
        'LoadingCityIDs': [city_ids.get(addr, "Не указано") for addr in loading_addresses],
        'UnloadingCityIDs': [city_ids.get(addr, "Не указано") for addr in unloading_addresses]
    }

    logging.info(f"Распарсенные данные заявки: {json.dumps(parsed_data, ensure_ascii=False, indent=4)}")

    # Добавляем ID заявки в набор обработанных
    processed_ids.add(application_id)
    save_processed_ids(processed_ids)

    return parsed_data