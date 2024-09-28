import logging
import json
from api_client import fetch_city_ids
from data_manager import save_processed_ids
from .cargo_parser import parse_cargo_parameters
from .transport_parser import parse_transport_summary
from .route_parser import parse_route


def parse_application(application, processed_ids, authorization_token):
    """Обрабатывает заявку и возвращает структурированные данные."""
    application_id = application.get('Id', 'Не указано')

    # Проверяем, была ли заявка уже обработана
    if application_id in processed_ids:
        logging.info(f"Заявка с ID {application_id} уже обработана. Пропуск.")
        return None  # Или можно вернуть специальный маркер

    transport_summary = application.get('TransportSummary', 'Не указано')
    route = application.get('Route', 'Не указано')
    cargo_parameters = application.get('CargoParameters', 'Не указано')

    # Парсинг TransportSummary
    cargo_type, loading_type = parse_transport_summary(transport_summary)

    # Словари для сопоставления
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

    loading_type_mapping = {
        "Задняя": 4,
        "Задня": 4,
        "задняя": 4
    }

    # Получение CargoTypeID и LoadingTypeID
    cargo_type_id = cargo_type_mapping.get(cargo_type, "Не указано")
    loading_type_id = loading_type_mapping.get(loading_type, "Не указано")

    # Парсинг маршрута
    waypoints = parse_route(route)

    # Обработка CargoParameters
    cargo_weight, cargo_value = parse_cargo_parameters(cargo_parameters)

    # Разделяем адреса на загрузочные и выгрузочные
    unique_loading_addresses = set(addr['address'] for addr in waypoints if addr['type'] == 'loading')
    unique_unloading_addresses = set(addr['address'] for addr in waypoints if addr['type'] == 'unloading')

    logging.info(f"Уникальные адреса для загрузки: {unique_loading_addresses}")
    logging.info(f"Уникальные адреса для выгрузки: {unique_unloading_addresses}")

    # Получаем CityID для всех адресов
    city_ids = fetch_city_ids(
        unique_loading_addresses=unique_loading_addresses,
        unique_unloading_addresses=unique_unloading_addresses,
        authorization_token=authorization_token
    )
    logging.debug(f"Полученные city_ids: {json.dumps(city_ids, ensure_ascii=False, indent=4)}")

    # Назначаем city_id каждой точке маршрута
    for wp in waypoints:
        wp['city_id'] = city_ids.get(wp['address'], "Не указано")

    parsed_data = {
        'Id': application_id,
        'Number': application.get('Number', 'Не указано'),
        'InitCost': application.get('InitCostDec', 'Не указано'),
        'ProductType': application.get('Cargo', 'Не указано'),
        'CargoParameters': cargo_parameters,
        'CargoWeight': cargo_weight,
        'CargoValue': cargo_value,
        'CargoType': cargo_type,
        'CargoTypeID': cargo_type_id,
        'LoadingType': loading_type,
        'LoadingTypeID': loading_type_id,
        'WayPoints': waypoints
    }

    logging.info(f"Распарсенные данные заявки: {json.dumps(parsed_data, ensure_ascii=False, indent=4)}")

    # Добавляем ID заявки в набор обработанных
    processed_ids.add(application_id)
    save_processed_ids(processed_ids)

    return parsed_data