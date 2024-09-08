## Создание и активация виртуального окружения

```bash
python -m venv venv
venv\Scripts\activate
```

## Установка зависимостей


```bash
pip install -r requirements.txt
```

## Установка переменных

Создайте файл .env, пример содержимого

```code
API_BASE_HOST = "https://testdev2.logistpro.su"
API_BASE_URL = f"{API_BASE_HOST}/api/v1/"
API_KEY = "cCwnQ8BxKCMlPsN7thVhdtou2PiJzZE46atEQwlehaQ="
LOGIN = "ext.customer.7@logistpro.su"
PASSWORD = "SY61kIX4v6Kk3K"
```

## Установка credential для гугл таблиц

1. Создать проект в Google Cloud Console
2. Включить Google Sheets API для вашего проекта.
3. Создайте учетные данные OAuth 2.0 и получите файл credentials.json
4. Выдать доступ к таблице боту, почта в файле credentials.json

## Запуск скрипта


```bash
python main.py
```


