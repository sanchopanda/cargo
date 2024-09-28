def build_ati_waypoints(waypoints, parsed_application):
    """Создает список waypoints для ATI API с добавлением информации о грузе."""
    ati_waypoints = []
    for wp in waypoints:
        way_point = {
            "type": wp.get('type', 'Не указано'),
            "city_id": wp.get('city_id', 'Не указано'),
            "address": wp.get('address', 'Не указано'),
            "location": {
                "type": "manual",
                "city_id": wp.get('city_id', 'Не указано'),
                "address": wp.get('address', 'Не указано')
            },
            "dates": {
                "type": "ready",
                "time": {
                    "type": "bounded",
                    "start": wp.get("time_start", "Не указано"),
                    "end": wp.get("time_end", "Не указано") if wp.get("time_end") else None
                },
                "first_date": wp.get("date", "Не указано")
            }
        }

        # Добавляем информацию о грузе для загрузочных точек
        if wp.get('type') == 'loading':
            way_point["cargos"] = [
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

        ati_waypoints.append(way_point)

    return ati_waypoints