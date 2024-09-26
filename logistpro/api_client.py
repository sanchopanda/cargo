import requests
import json
import logging
import os
from config import ATI_API_URL
from dotenv import load_dotenv

load_dotenv()

def fetch_city_ids(unique_loading_addresses, unique_unloading_addresses, authorization_token=os.getenv("AUTHORIZATION_TOKEN")):
    """
    Получает CityID для списка адресов через ATI API.

    Args:
        unique_loading_addresses (set): Множество уникальных адресов для погрузки.
        unique_unloading_addresses (set): Множество уникальных адресов для выгрузки.
        authorization_token (str): Токен авторизации для API.

    Returns:
        Dict[str, int]: Словарь, где ключ - адрес, значение - CityID или "Не указано".
    """
    headers = {
        "Authorization": f"Bearer {authorization_token}",
        "Content-Type": "application/json"
    }

    # Формируем тело запроса
    body = list(unique_loading_addresses) + list(unique_unloading_addresses)
    logging.info(f"Запрос к API с телом: {json.dumps(body, ensure_ascii=False)}")

    try:
        response = requests.post(ATI_API_URL, headers=headers, data=json.dumps(body), timeout=15)
        if response.status_code == 200:
            data = response.json()
            logging.info(f"Ответ от API: {json.dumps(data, ensure_ascii=False, indent=4)}")

            city_id_mapping = {}
            for address in body:
                address_info = data.get(address, {})
                if address_info.get('is_success'):
                    city_id = address_info.get('city_id', "Не указано")
                    city_id_mapping[address] = city_id
                else:
                    city_id_mapping[address] = "Не указано"
            return city_id_mapping
        else:
            logging.error(f"Ошибка при запросе к ATI API: {response.status_code} - {response.text}")
            return {address: "Не указано" for address in body}
    except requests.RequestException as e:
        logging.error(f"Исключение при запросе к ATI API: {e}")
        return {address: "Не указано" for address in body}