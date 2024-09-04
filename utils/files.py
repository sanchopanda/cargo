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

    