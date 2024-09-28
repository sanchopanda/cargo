import os
import logging
from .converter import convert_to_single
from .waypoints_builder import build_ati_waypoints

def create_request_body(parsed_application):
    """Создает тело запроса на основе распарсенных данных заявки."""
    try:
        waypoints = parsed_application.get('WayPoints', [])
        ati_waypoints = build_ati_waypoints(waypoints, parsed_application)

        loading_waypoints = [wp for wp in ati_waypoints if wp.get('type') == 'loading']
        unloading_waypoints = [wp for wp in ati_waypoints if wp.get('type') == 'unloading']

        # Обработка way_points согласно требованиям
        if len(ati_waypoints) > 2:
            processed_waypoints = ati_waypoints[1:-1]
        else:
            processed_waypoints = None

        route = {
            "loading": loading_waypoints[0] if loading_waypoints else {},
            "unloading": unloading_waypoints[-1] if unloading_waypoints else {},
            "is_round_trip": False
        }

        if processed_waypoints:
            route["way_points"] = processed_waypoints

        request_body = {
            "cargo_application": {
                "external_id": parsed_application.get('Id', 'Не указано'),
                "route": route,
                "truck": {
                    "trucks_count": 1,
                    "load_type": "ftl",
                    "body_types": parsed_application.get('CargoTypeID', 'Не указано'),
                    "body_loading": {
                        "types": parsed_application.get('LoadingTypeID', 'Не указано'),
                        "is_all_required": True
                    },
                    "body_unloading": {
                        "types": parsed_application.get('LoadingTypeID', 'Не указано'),
                        "is_all_required": True
                    },
                    "documents": {
                        "tir": True,
                        "cmr": True,
                        "t1": False,
                        "medical_card": False
                    },
                    "requirements": {
                        "logging_truck": False,
                        "road_train": False,
                        "air_suspension": True
                    },
                    "adr": 3,
                    "belts_count": 4,
                    "is_tracking": True,
                    "required_capacity": 15
                },
                "payment": {
                    "cash": convert_to_single(parsed_application.get('InitCost', 'Не указано')),
                    "type": "without-bargaining",
                    "currency_type": 1,
                    "hide_counter_offers": True,
                    "direct_offer": False,
                    "prepayment": {
                        "percent": 50,
                        "using_fuel": True
                    },
                    "payment_mode": {
                        "type": "delayed-payment",
                        "payment_delay_days": 7
                    },
                    "accept_bids_with_vat": True,
                    "accept_bids_without_vat": False,
                    "vat_percents": 20,
                    "start_rate": convert_to_single(parsed_application.get('InitCost', 'Не указано')),
                    "auction_currency_type": 1,
                    "bid_step": 10,
                    "auction_duration": {
                        "fixed_duration": "1h",
                    },
                    "accept_counter_offers": True,
                    "auto_renew": {
                        "enabled": True,
                        "renew_interval": 24
                    },
                    "is_antisniper": False,
                    "rate_rise": {
                        "interval": 1,
                        "rise_amount": 5
                    },
                    "winner_criteria": "best-rate",
                    "time_to_provide_documents": {
                        "hours": 48
                    },
                    "winner_reselection_count": 2,
                    "auction_restart": {
                        "enabled": True,
                        "restart_interval": 24
                    },
                    "no_winner_end_options": {
                        "type": "archive"
                    },
                    "rates": {
                        "cash": convert_to_single(parsed_application.get('InitCost', 'Не указано')),
                        "rate_with_nds": convert_to_single(parsed_application.get('InitCost', 'Не указано')),
                        "rate_without_nds": convert_to_single(parsed_application.get('InitCost', 'Не указано'))
                    }
                },
                "boards": [
                    {
                        "id": os.getenv('BOARD_ID', 'Не указано'),
                        "publication_mode": "now",
                        "cancel_publish_on_auction_bet": False,
                        "reservation_enabled": True
                    }
                ],
                "note": f"{convert_to_single(parsed_application.get('Id', 'Не указано'))}",
                "contacts": [0]
            }
        }

        return request_body
    except KeyError as e:
        logging.error(f"Отсутствует ключ: {e} в parsed_application: {parsed_application.get('Id', 'Не указано')}")
        return None
    except Exception as e:
        logging.exception(f"Неизвестная ошибка при создании тела запроса для заявки: {parsed_application.get('Id', 'Не указано')}: {e}")
        return None