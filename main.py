import os
import time
import argparse
from dotenv import load_dotenv
from api.api import check_api_access, login, get_requests_data, fetch_request
from utils.files import save_request_to_file, save_to_file
from utils.google_sheets import init_google_sheets, update_google_sheet
from utils.files import read_processed_ids, write_processed_id

load_dotenv()

LOGIN = os.getenv('LOGIN')
PASSWORD = os.getenv('PASSWORD')
SPREADSHEET_NAME = 'Logist Pro'
ID_FILE = 'processed_ids.json'  # Файл для хранения обработанных ID в формате JSON

def process_requests(write_to_sheet=False):
    if not check_api_access():
        print("   >> API не доступен")
        return
    print("   >> есть доступ")

    if not login({"Login": LOGIN, "Password": PASSWORD}):
        print("   >> Авторизация не удалась")
        return
    print("   >> Авторизация прошла успешно")

    # Получение данных заявок
    requests_data = get_requests_data()
    if requests_data:
        save_to_file("response.json", requests_data)

        # Чтение уже обработанных ID
        processed_ids = read_processed_ids(ID_FILE)

        # Извлекаем ID всех заявок
        ids = [item["Id"] for item in requests_data.get("Items", [])]
        for id in ids:
            # Проверяем, обработан ли ID ранее
            if id not in processed_ids:
                request_data = fetch_request(id)
                if request_data:
                    save_request_to_file(id, request_data)
                    write_processed_id(ID_FILE, id)  # Добавляем новый ID в файл
                    print(f"   >> Заявка {id} успешно обработана и добавлена.")
            else:
                print(f"   >> Заявка {id} уже была обработана ранее.")

    if write_to_sheet:
        worksheet = init_google_sheets(SPREADSHEET_NAME)
        if worksheet:
            requests_dir = os.path.join(os.getcwd(), 'requests')
            update_google_sheet(worksheet, requests_dir)

def main(write_to_sheet=False, cycle=False, interval=5):
    while True:
        process_requests(write_to_sheet)

        if not cycle:
            break

        print(f"   >> Ожидание {interval} минут до следующего запуска...")
        time.sleep(interval * 60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Скрипт обработки заявок и работы с Google Sheets')
    parser.add_argument('--write-to-sheet', action='store_true', help='Включить логику работы с Google Sheets')
    parser.add_argument('--cycle', action='store_true', help='Запускать скрипт циклично')
    parser.add_argument('--interval', type=int, default=5, help='Интервал между циклами в минутах (по умолчанию 5 минут)')

    args = parser.parse_args()

    main(write_to_sheet=args.write_to_sheet, cycle=args.cycle, interval=args.interval)

