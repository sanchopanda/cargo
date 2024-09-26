from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from cookie_manager import save_cookies
from config import LOGIN_URL, MAIN_URL, CHROME_DRIVER_PATH, SELENIUM_WAIT_TIMEOUT
from dotenv import load_dotenv

load_dotenv()

def login_and_save_cookies(cookie_file):
    """Функция для авторизации через Selenium и сохранения кук.

    Args:
        cookie_file (str): Путь к файлу для сохранения кук.
    """
    # Настройки драйвера Chrome
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # запуск без интерфейса, если нужно
    service = Service(executable_path=CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(LOGIN_URL)  # URL страницы входа

    # Ввод логина и пароля
    username = driver.find_element(By.ID, "UserName")
    password = driver.find_element(By.ID, "Password")
    username.send_keys(os.getenv("USERNAME"))
    password.send_keys(os.getenv("PASSWORD"))

    # Дождаться вручную прохождения капчи и нажатия на кнопку входа
    print("Пройдите капчу и нажмите 'Войти'.")

    try:
        # Ожидаем, что после авторизации браузер перейдет на главную страницу
        WebDriverWait(driver, SELENIUM_WAIT_TIMEOUT).until(
            EC.url_to_be(MAIN_URL)  # Проверяем переход на URL главной страницы
        )
        print("Авторизация прошла успешно!")
    except:
        print("Таймаут ожидания или авторизация не удалась. Проверьте корректность действий.")

    # Сохраняем куки после успешного перехода
    save_cookies(driver, cookie_file)
    driver.quit()