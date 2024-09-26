# config.py

import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Пути к файлам
PROCESSED_IDS_FILE = 'processed_ids.json'
COOKIE_FILE = 'cookies.pkl'

# URL-ы
ATI_API_URL = "https://api.ati.su/v1.0/dictionaries/locations/parse"
DATA_URL = "https://lk.logistpro.su/api/public/request?mode=Open&tenderType=Order&public=Show"
LOGIN_URL = "https://lk.logistpro.su/Account/Login"
MAIN_URL = "https://lk.logistpro.su/"

# Авторизационный токен
AUTHORIZATION_TOKEN = '83b0d3bc20244d56a43404e9b8fe694a'  # Замените на актуальный токен

# Путь к драйверу Chrome
CHROME_DRIVER_PATH = r'/chromedriver-win64/chromedriver.exe'

# Настройки Selenium
SELENIUM_WAIT_TIMEOUT = 300  # Время ожидания в секундах


