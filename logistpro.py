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

class LogistProParser:
    def __init__(self):
        # Загрузка переменных окружения
        load_dotenv()
        self.LOGIN = os.getenv('LOGIN')
        self.PASSWORD = os.getenv('PASSWORD')
        
        # Настройка браузера
        options = Options()
        options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.wait = WebDriverWait(self.driver, 40)

        # Список обработанных заявок
        self.processed_orders = self.load_processed_orders()

    def login(self):
        """Метод для авторизации на сайте."""
        # Переход на страницу авторизации
        self.driver.get("https://lk.logistpro.su/Account/Login")

        # Ввод логина и пароля
        username = self.driver.find_element(By.ID, "UserName")
        password = self.driver.find_element(By.ID, "Password")
        username.send_keys(self.LOGIN)
        password.send_keys(self.PASSWORD)

        # Ожидание успешной авторизации
        print("Пожалуйста, нажмите кнопку входа и пройдите капчу.")
        while True:
            if self.driver.current_url == "https://lk.logistpro.su/":
                print("Успешная авторизация!")
                break
            else:
                print("Ожидание авторизации...")
                time.sleep(5)

    def get_orders(self):
        """Метод для получения и парсинга заявок, возвращает словарь с данными заявок."""
        print("Переход на страницу заявок...")
        self.driver.get("https://lk.logistpro.su/Requests/Open")

        # Ожидание загрузки элементов заявок
        try:
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "summary-tender-row")))
            print("Элементы заявок успешно загружены.")
        except Exception as e:
            print(f"Ошибка при загрузке заявок: {e}")
            return {}

        # Поиск всех заявок
        try:
            orders = self.driver.find_elements(By.CLASS_NAME, "summary-tender-row")
            print(f"Найдено {len(orders)} заявок")
        except Exception as e:
            print(f"Ошибка при поиске заявок: {e}")
            return {}

        # Создаем словарь для хранения данных заявок
        orders_data = {}

        if not orders:
            print("Нет доступных заявок для обработки.")
            return {}

        for order in orders:
            try:
                order_data = self.process_order(order)
                if order_data:
                    order_id = order_data['order_id']
                    orders_data[order_id] = order_data
            except Exception as e:
                print(f"Ошибка при обработке заявки: {e}")

        # Возвращаем словарь с данными заявок
        return orders_data

    def process_order(self, order):
        """Метод для обработки одной заявки и возврата данных в виде словаря."""
        try:
            order_id_element = order.find_element(By.CLASS_NAME, "tight")
            order_id = order_id_element.text.split('\n')[0].strip()

            # Проверка, не была ли заявка уже обработана
            if order_id in self.processed_orders:
                print(f"Заявка {order_id} уже обработана, пропускаем.")
                return None

            # Получение данных заявки
            weight, volume, body_type, cargo_type = self.get_order_details(order)
            loading_date, loading_address, loading_start_time, loading_end_time = self.get_loading_info()
            unloading_date, unloading_address, unloading_start_time, unloading_end_time = self.get_unloading_info()
            bid = self.get_bid(order)

            # Формируем словарь с данными заявки
            order_data = {
                "order_id": order_id,
                "weight": weight,
                "volume": volume,
                "body_type": body_type,
                "cargo_type": cargo_type,
                "loading_date": loading_date,
                "loading_start_time": loading_start_time,
                "loading_end_time": loading_end_time,
                "loading_address": loading_address,
                "unloading_date": unloading_date,
                "unloading_start_time": unloading_start_time,
                "unloading_end_time": unloading_end_time,
                "unloading_address": unloading_address,
                "bid": bid
            }

            # Сохранение заявки как обработанной
            self.processed_orders.append(order_id)
            self.save_processed_orders(self.processed_orders)

            return order_data
        except Exception as e:
            print(f"Ошибка при обработке заявки: {e}")
            return None

    def get_order_details(self, order):
        """Метод для получения деталей заявки."""
        try:
            fixed_divs = order.find_elements(By.CLASS_NAME, "fixed")
            if len(fixed_divs) > 0:
                weight_volume_text = fixed_divs[0].text.split("\n")[0]
                weight = weight_volume_text.split('т.')[0].strip() if 'т' in weight_volume_text else "Не указано"
                volume = weight_volume_text.split('т. ')[1].split('м³')[0].strip() if 'м³' in weight_volume_text else "Не указано"
                body_type = fixed_divs[0].text.split("\n")[1].strip() if len(fixed_divs[0].text.split("\n")) > 1 else "Не указано"
                cargo_type = fixed_divs[0].text.split("\n")[2].strip() if len(fixed_divs[0].text.split("\n")) > 2 else "Не указано"
                return weight, volume, body_type, cargo_type
        except Exception as e:
            print(f"Ошибка при получении деталей заявки: {e}")
        return "Не указано", "Не указано", "Не указано", "Не указано"

    def get_loading_info(self):
        """Метод для получения информации о загрузке."""
        try:
            loading_element = self.driver.find_element(By.XPATH, "//span[@data-title='Погрузка']/parent::div")
            loading_date = loading_element.text.split('\n')[0]
            loading_address = self.driver.find_element(By.XPATH, "//span[@data-title='Погрузка']/following::div[1]").get_attribute("title")
            loading_date_formatted, loading_start_time, loading_end_time = self.format_dates(loading_date)
            return loading_date_formatted, loading_address, loading_start_time, loading_end_time
        except NoSuchElementException:
            return "Даты загрузки нет", "Адреса загрузки нет", "Время не указано", "Время не указано"

    def get_unloading_info(self):
        """Метод для получения информации о разгрузке."""
        try:
            unloading_element = self.driver.find_element(By.XPATH, "//span[@data-title='Выгрузка']/parent::div")
            unloading_date = unloading_element.text.split('\n')[0]
            unloading_address = self.driver.find_element(By.XPATH, "//span[@data-title='Выгрузка']/following::div[1]").get_attribute("title")
            unloading_date_formatted, unloading_start_time, unloading_end_time = self.format_dates(unloading_date)
            return unloading_date_formatted, unloading_address, unloading_start_time, unloading_end_time
        except NoSuchElementException:
            return "Даты разгрузки нет", "Адреса разгрузки нет", "Время не указано", "Время не указано"

    def get_bid(self, order):
        """Метод для получения ставки."""
        try:
            bid_text = order.find_elements(By.CLASS_NAME, "ajaxLink")[1].text
            return bid_text.replace("\u00a0", "").replace(" ", "").replace("₽", "")
        except NoSuchElementException:
            return "Ставка не указана"

    def format_dates(self, date_str):
        """Метод для форматирования дат."""
        try:
            date_part, time_part = date_str.split(maxsplit=1)
            date_formatted = datetime.strptime(date_part, "%d.%m.%Y").strftime("%Y-%m-%d")
            if '-' in time_part:
                time_start, time_end = time_part.split('-')
                return date_formatted, time_start.strip(), time_end.strip()
            return date_formatted, time_part.strip(), "Время окончания не указано"
        except ValueError as e:
            print(f"Ошибка при форматировании даты: {e}")
            return "Неверный формат даты", "Время не указано", "Время не указано"

    def load_processed_orders(self, filename='processed_orders.json'):
        """Загрузка обработанных заявок из файла."""
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_processed_orders(self, processed_orders, filename='processed_orders.json'):
        """Сохранение обработанных заявок в файл."""
        with open(filename, 'w') as f:
            json.dump(processed_orders, f, indent=4)

    def close(self):
        """Закрытие драйвера."""
        self.driver.quit()


# Пример использования класса:
parser = LogistProParser()
parser.login()
orders_data = parser.get_orders()

print(orders_data)

parser.close()
