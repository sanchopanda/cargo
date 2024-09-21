from datetime import datetime
import time
import json
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException 

load_dotenv()

LOGIN = os.getenv('LOGIN')
PASSWORD = os.getenv('PASSWORD')

# Функция для форматирования дат
def format_dates(date_str):
    try:
        # Разделяем строку на дату и время, если есть
        date_part, time_part = date_str.split(maxsplit=1)
        
        # Преобразуем дату в формат yyyy-mm-dd
        date_formatted = datetime.strptime(date_part, "%d.%m.%Y").strftime("%Y-%m-%d")
        
        # Если время указано, разделяем его на начальное и конечное
        if '-' in time_part:
            time_start, time_end = time_part.split('-')
            time_start = time_start.strip()
            time_end = time_end.strip()
        else:
            time_start = time_part.strip()
            time_end = "Время окончания не указано"

        return date_formatted, time_start, time_end
    except ValueError as e:
        print(f"Ошибка при форматировании даты: {e}")
        return "Неверный формат даты", "Время начала не указано", "Время окончания не указано"

# Функция для загрузки обработанных заявок из json файла
def load_processed_orders(filename='processed_orders.json'):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Функция для сохранения обработанных заявок в json файл
def save_processed_orders(processed_orders, filename='processed_orders.json'):
    with open(filename, 'w') as f:
        json.dump(processed_orders, f, indent=4)

# Настройки браузера
options = Options()
options.add_argument("--start-maximized")

# Инициализация вебдрайвера
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Инициализация ожидания WebDriverWait
wait = WebDriverWait(driver, 40)  # Устанавливаем ожидание на 40 секунд


# Переход на страницу авторизации
driver.get("https://lk.logistpro.su/Account/Login")

# Ввод логина и пароля
username = driver.find_element(By.ID, "UserName")
password = driver.find_element(By.ID, "Password")

# Замените эти данные на ваши актуальные данные для входа
username.send_keys(LOGIN)
password.send_keys(PASSWORD)

# Информируем пользователя, чтобы он сам нажал кнопку и прошел капчу
print("Пожалуйста, нажмите кнопку входа и пройдите капчу.")

# Ожидание пользователя
while True:
    # Проверяем, находимся ли мы на главной странице (после успешного логина)
    if driver.current_url == "https://lk.logistpro.su/":
        print("Успешная авторизация!")
        break
    else:
        print("Ожидание авторизации...")
        time.sleep(5)  # Проверяем каждые 5 секунд

# Переход на страницу заявок
print("Переход на страницу заявок...")
driver.get("https://lk.logistpro.su/Requests/Open")

# Используем явное ожидание для загрузки элементов заявок
try:
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "summary-tender-row")))
    print("Элементы заявок успешно загружены.")
except Exception as e:
    print(f"Ошибка при загрузке заявок: {e}")


# Загрузка обработанных заявок
processed_orders = load_processed_orders()

# Поиск всех заявок
try:
    orders = driver.find_elements(By.CLASS_NAME, "summary-tender-row")
    print(f"Найдено {len(orders)} заявок")
except Exception as e:
    print(f"Ошибка при поиске заявок: {e}")

if not orders:
    print("Нет доступных заявок для обработки.")
else:
    for order in orders:
        try:
            order_id_element = order.find_element(By.CLASS_NAME, "tight")
            order_id = order_id_element.text.split('\n')[0].strip()

            # Проверка, не была ли заявка уже обработана
            if order_id in processed_orders:
                print(f"Заявка {order_id} уже обработана, пропускаем.")
                continue

            # Примерное количество элементов в div с фиксированным расположением
            fixed_divs = order.find_elements(By.CLASS_NAME, "fixed")

            if len(fixed_divs) > 0:
                weight_volume_text = fixed_divs[0].text.split("\n")[0]
                
                # Проверяем, содержится ли информация о весе и объеме
                if 'т' in weight_volume_text and 'м³' in weight_volume_text:
                    weight = weight_volume_text.split('т.')[0].strip()
                    volume = weight_volume_text.split('т. ')[1].split('м³')[0].strip()
                else:
                    weight = "Не указано"
                    volume = "Не указано"

                # Тип кузова и тип груза
                body_type = fixed_divs[0].text.split("\n")[1].strip() if len(fixed_divs[0].text.split("\n")) > 1 else "Не указано"
                cargo_type = fixed_divs[0].text.split("\n")[2].strip() if len(fixed_divs[0].text.split("\n")) > 2 else "Не указано"
            else:
                print(f"Недостаточно данных для заявки {order_id}, пропускаем.")
                continue

             # Логика для загрузки и выгрузки
            try:
                loading_element = driver.find_element(By.XPATH, "//span[@data-title='Погрузка']/parent::div")
                loading_date = loading_element.text.split('\n')[0]
                loading_address = driver.find_element(By.XPATH, "//span[@data-title='Погрузка']/following::div[1]").get_attribute("title")
                
                # Применяем форматирование к дате загрузки
                loading_date_formatted, loading_start_time, loading_end_time = format_dates(loading_date)
            except NoSuchElementException:
                loading_date_formatted = "Даты загрузки нет"
                loading_start_time = loading_end_time = "Время загрузки не указано"
                loading_address = "Адреса загрузки нет"

            try:
                unloading_element = driver.find_element(By.XPATH, "//span[@data-title='Выгрузка']/parent::div")
                unloading_date = unloading_element.text.split('\n')[0]
                unloading_address = driver.find_element(By.XPATH, "//span[@data-title='Выгрузка']/following::div[1]").get_attribute("title")
                
                # Применяем форматирование к дате выгрузки
                unloading_date_formatted, unloading_start_time, unloading_end_time = format_dates(unloading_date)
            except NoSuchElementException:
                unloading_date_formatted = "Даты разгрузки нет"
                unloading_start_time = unloading_end_time = "Время разгрузки не указано"
                unloading_address = "Адреса разгрузки нет"

            # Получаем ставку
            try:
                 bid_text = order.find_elements(By.CLASS_NAME, "ajaxLink")[1].text
                 bid = bid_text.replace("\u00a0", "").replace(" ", "").replace("₽", "")
            except NoSuchElementException:
                 bid = "Ставка не указана"

            # Выводим данные заявки
            print(f"ID: {order_id}")
            print(f"Вес: {weight} т")
            print(f"Объем: {volume} м³")
            print(f"Тип кузова: {body_type}")
            print(f"Тип груза: {cargo_type}")
            print(f"Дата загрузки: {loading_date_formatted}")
            print(f"Время начала загрузки: {loading_start_time}")
            print(f"Время окончания загрузки: {loading_end_time}")
            print(f"Адрес загрузки: {loading_address}")
            print(f"Дата разгрузки: {unloading_date_formatted}")
            print(f"Время начала разгрузки: {unloading_start_time}")
            print(f"Время окончания разгрузки: {unloading_end_time}")
            print(f"Адрес разгрузки: {unloading_address}")
            print(f"Ставка: {bid}")
            print("-" * 50)

            # Добавляем заявку в список обработанных
            processed_orders.append(order_id)
            save_processed_orders(processed_orders)

        except Exception as e:
            print(f"Ошибка при обработке заявки: {e}")
            continue

# Закрытие браузера
driver.quit()
