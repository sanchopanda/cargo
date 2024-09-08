import os
import json

def save_request_to_file(id, request_data):
    dir_path = os.path.join(os.getcwd(), 'requests')
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    file_path = os.path.join(dir_path, f"{id}.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(request_data, f, ensure_ascii=False, indent=2)
    print(f"Request saved to {file_path}")

def save_to_file(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Response saved to {filename}")


import json
import os

def read_processed_ids(file_path):
    if not os.path.exists(file_path):
        return []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            return []


def write_processed_id(file_path, new_id):
    processed_ids = read_processed_ids(file_path)
    
    if new_id not in processed_ids:
        processed_ids.append(new_id)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(processed_ids, f, ensure_ascii=False, indent=4)
