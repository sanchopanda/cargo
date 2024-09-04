import os
import json
import gspread
from google.oauth2.service_account import Credentials

def init_google_sheets(spreadsheet_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    creds_path = os.path.join(script_dir, '../credentials.json')
    
    if not os.path.exists(creds_path):
        print("   >> Google Sheets credentials file not found, skipping Google Sheets update.")
        return None

    scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
    client = gspread.authorize(creds)
    spreadsheet = client.open(spreadsheet_name)
    return spreadsheet.sheet1  # Открываем первый лист

def update_google_sheet(worksheet, requests_dir):
    headers = ['Id', 'Дата', 'Тип груза', 'Загрузка', 'Выгрузка', 'Кузов', 'Ставка', 'Фирма', 'Город', 'ФИО', 'Телефон']
    worksheet.append_row(headers)

    for filename in os.listdir(requests_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(requests_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                row = process_data_for_sheet(data)
                worksheet.append_row(row)

def process_data_for_sheet(data):
    from utils.utils import extract_body_type, extract_city
    id = data.get('Id', '')
    start_date = data.get('StartDate', '')
    cargo = data.get('Cargo', '')
    addresses_loading = [route['Address'] for route in data.get('Route', []) if route.get('TypeTitle') == 'Погрузка']
    addresses_unloading = [route['Address'] for route in data.get('Route', []) if route.get('TypeTitle') == 'Выгрузка']
    transport_summary = data.get('TransportSummary', '')

    proposal = data.get('Proposal', {})
    bet_dec = proposal.get('BetDec', '') if proposal else ''
    company_name = data.get('Customer', {}).get('Company', {}).get('Name', '')
    city = extract_city(data.get('Customer', {}).get('Company', {}).get('AddressLegal', ''))
    contact_person = data.get('Customer', {}).get('ContactPerson', {})
    contact_name = contact_person.get('Name', '')
    contact_phone = contact_person.get('Phone', '')

    return [
        id,
        start_date,
        cargo,
        ', '.join(addresses_loading),
        ', '.join(addresses_unloading),
        extract_body_type(transport_summary),
        bet_dec,
        company_name,
        city,
        contact_name,
        contact_phone
    ]

