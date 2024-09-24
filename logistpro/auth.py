from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from cookie_manager import save_cookies

# Функция для авторизации через Selenium и сохранения кук
def login_and_save_cookies(cookie_file):
    # Настройки драйвера Chrome
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # запуск без интерфейса, если нужно
    service = Service(executable_path=r'C:/Users/Даниил/Documents/GitHub/logistpro/chromedriver-win64/chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get("https://lk.logistpro.su/Account/Login")  # URL страницы входа

    # Ввод логина и пароля
    username = driver.find_element(By.ID, "UserName")
    password = driver.find_element(By.ID, "Password")
    username.send_keys("logist@fortuna-aero.ru")
    password.send_keys("6852Fbddeaf5416f")

    # Дождаться вручную прохождения капчи и нажатия на кнопку входа
    print("Пройдите капчу и нажмите 'Войти'.")
    
    try:
        # Ожидаем, что после авторизации браузер перейдет на главную страницу
        WebDriverWait(driver, 300).until(
            EC.url_to_be("https://lk.logistpro.su/")  # Проверяем переход на URL главной страницы
        )
        print("Авторизация прошла успешно!")
    except:
        print("Таймаут ожидания или авторизация не удалась. Проверьте корректность действий.")

    # Сохраняем куки после успешного перехода
    save_cookies(driver, cookie_file)
    driver.quit()
