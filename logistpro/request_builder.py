import os

def convert_to_single(value):
    """
    Преобразует список с одним элементом в одиночное значение.
    Если значение не список или список содержит более одного элемента, возвращает его без изменений.
    
    Args:
        value (any): Значение для преобразования.
        
    Returns:
        any: Преобразованное значение.
    """
    if isinstance(value, list):
        if len(value) == 1:
            return value[0]
    return value

def create_request_body(parsed_application):
    """Создает тело запроса на основе распарсенных данных заявки.

    Args:
        parsed_application (dict): Распарсенные данные заявки.

    Returns:
        dict: Тело запроса в формате JSON.
    """
    # Применяем преобразование к нужным полям
    loading_dates = convert_to_single(parsed_application.get('LoadingDates', []))
    unloading_dates = convert_to_single(parsed_application.get('UnloadingDates', []))
    
    loading_time_starts = convert_to_single(parsed_application.get('LoadingTimeStarts', []))
    loading_time_ends = convert_to_single(parsed_application.get('LoadingTimeEnds', []))
    unloading_time_starts = convert_to_single(parsed_application.get('UnloadingTimeStarts', []))
    unloading_time_ends = convert_to_single(parsed_application.get('UnloadingTimeEnds', []))
    
    request_body = {
        "cargo_application": {
            "external_id": parsed_application.get('Id', 'Не указано'),
            "route": {
                "loading": {
                    "city_id": parsed_application.get('LoadingCityIDs', []),
                    "address": parsed_application.get('LoadingAddresses', []),
                    "location": {
                        "type": "manual",
                        "city_id": parsed_application.get('LoadingCityIDs', []),
                        "address": parsed_application.get('LoadingAddresses', [])
                    },
                    "dates": {
                        "type": "ready",
                        "time": {
                            "type": "bounded",
                            "start": loading_time_starts,
                            "end": loading_time_ends
                        },
                        "first_date": loading_dates
                    },
                    "cargos": [
                        {
                            "id": parsed_application.get('CargoTypeID', 'Не указано'),
                            "name": parsed_application.get('CargoType', 'Не указано'),
                            "weight": {
                                "type": "tons",
                                "quantity": parsed_application.get('CargoWeight', 'Не указано')
                            },
                            "volume": {
                                "quantity": parsed_application.get('CargoValue', 'Не указано')
                            }
                        }
                    ]
                },
                "unloading": {
                    "city_id": parsed_application.get('UnloadingCityIDs', []),
                    "address": parsed_application.get('UnloadingAddresses', []),
                    "location": {
                        "type": "manual",
                        "city_id": parsed_application.get('UnloadingCityIDs', []),
                        "address": parsed_application.get('UnloadingAddresses', [])
                    },
                    "dates": {
                        "type": "ready",
                        "time": {
                            "type": "bounded",
                            "start": unloading_time_starts,
                            "end": unloading_time_ends
                        },
                        "first_date": unloading_dates
                    }
                },
                "is_round_trip": False
            },
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
                    "end_time": "2024-09-21T12:00:00.000Z"
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
            "note": f"{convert_to_single(parsed_application.get('InitCost', 'Не указано'))}",
            "contacts": [0]
        }
    }
    return request_body