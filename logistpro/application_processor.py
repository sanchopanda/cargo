import logging
import json
from parser import parse_application
from request_builder import create_request_body
from data_manager import load_processed_ids, save_processed_ids

def process_applications(data, authorization_token):
    """Обрабатывает список заявок и создает тела запросов.

    Args:
        data (dict): Сырые данные с заявками.
        authorization_token (str): Токен авторизации для API.

    Returns:
        tuple: Словарь распарсенных заявок и словарь тел запросов.
    """
    processed_ids = load_processed_ids()
    applications_dict = {}
    request_bodies = {}  # Словарь для хранения тел запросов

    for application in data.get('Items', []):
        parsed_application = parse_application(application, processed_ids, authorization_token)
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
    return applications_dict, request_bodies