# Coursework Transactions

Курсовая работа по анализу банковских транзакций из Excel-файла.

## Описание

Приложение читает транзакции из Excel-файла, формирует JSON-ответы для веб-страниц, выполняет сервисный поиск по операциям и создает отчеты.

## Структура проекта

```text
src/
  utils.py
  views.py
  services.py
  reports.py
  main.py

data/
  operations.xlsx

tests/
  test_utils.py
  test_views.py
  test_services.py
  test_reports.py

user_settings.json
```

## Реализованный функционал

### Веб-страница «Главная»

Функция `main_page` принимает дату и время в формате:

```text
YYYY-MM-DD HH:MM:SS
```

И возвращает JSON-ответ:

- приветствие по времени суток;
- информацию по картам;
- топ-5 транзакций;
- курсы валют;
- цены акций.

### Сервисы

В модуле `services.py` реализованы:

- `simple_search` — простой поиск по описанию и категории;
- `phone_number_search` — поиск транзакций с телефонными номерами;
- `transfers_to_individuals_search` — поиск переводов физическим лицам.

### Отчеты

В модуле `reports.py` реализованы:

- декоратор `report_to_file`;
- отчет `spending_by_category`.

Отчет показывает траты по выбранной категории за последние три месяца от переданной даты.

## Настройки пользователя

Файл `user_settings.json` содержит список валют и акций:

```json
{
  "user_currencies": ["USD", "EUR"],
  "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
}
```

## Установка зависимостей

```bash
poetry install
```

## Запуск демонстрации

```bash
poetry run python -m src.main
```

## Запуск тестов

```bash
poetry run pytest
```

## Проверка покрытия

```bash
poetry run pytest --cov=src --cov-report=html
```

## Проверка flake8

```bash
poetry run flake8 src tests
```

