import pickle

# Функция для сохранения кук в файл
def save_cookies(driver, path):
    cookies = driver.get_cookies()
    print("Куки для сохранения:", cookies)  # Отладка для проверки
    if cookies:
        with open(path, 'wb') as file:
            pickle.dump(cookies, file)
    else:
        print("Куки пустые. Авторизация могла завершиться неудачно.")

# Функция для загрузки кук из файла
def load_cookies(path):
    with open(path, 'rb') as file:
        return pickle.load(file)