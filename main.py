import os
from dotenv import load_dotenv
from api.api import check_api_access, login, get_requests_data, fetch_request
from utils.files import save_request_to_file, save_to_file
from utils.google_sheets import init_google_sheets, update_google_sheet

load_dotenv()

LOGIN = os.getenv('LOGIN')
PASSWORD = os.getenv('PASSWORD')
SPREADSHEET_NAME = 'Logist Pro'

def main():
    if not check_api_access():
        print("   >> API не доступен")
        return
    print("   >> есть доступ")

    if not login({"Login": LOGIN, "Password": PASSWORD}):
        print("   >> Авторизация не удалась")
        return
    print("   >> Авторизация прошла успешно")

    requests_data = get_requests_data()
    if requests_data:
        save_to_file("response.json", requests_data)
        ids = [item["Id"] for item in requests_data.get("Items", [])]
        for id in ids:
            request_data = fetch_request(id)
            if request_data:
                save_request_to_file(id, request_data)

    worksheet = init_google_sheets(SPREADSHEET_NAME)
    if worksheet:
        requests_dir = os.path.join(os.getcwd(), 'requests')
        update_google_sheet(worksheet, requests_dir)

if __name__ == "__main__":
    main()