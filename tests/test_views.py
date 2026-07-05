import json
from datetime import datetime
from typing import Any
from unittest.mock import patch

import pandas as pd

from src.views import (
    get_cards_info,
    get_greeting,
    get_top_transactions,
    main_page,
)


def test_get_greeting() -> None:
    """Тестирует приветствие по времени суток."""
    assert get_greeting(datetime(2021, 12, 31, 6, 0, 0)) == "Доброе утро"
    assert get_greeting(datetime(2021, 12, 31, 12, 0, 0)) == "Добрый день"
    assert get_greeting(datetime(2021, 12, 31, 18, 0, 0)) == "Добрый вечер"
    assert get_greeting(datetime(2021, 12, 31, 23, 0, 0)) == "Доброй ночи"


def test_get_cards_info() -> None:
    """Тестирует получение информации по картам."""
    dataframe = pd.DataFrame(
        {
            "Номер карты": ["*1234", "*1234", "*5678"],
            "Сумма платежа": [-100.0, -200.0, -50.0],
        }
    )

    result = get_cards_info(dataframe)

    assert result == [
        {
            "last_digits": "1234",
            "total_spent": 300.0,
            "cashback": 3.0,
        },
        {
            "last_digits": "5678",
            "total_spent": 50.0,
            "cashback": 0.5,
        },
    ]


def test_get_top_transactions() -> None:
    """Тестирует получение топ-5 транзакций."""
    dataframe = pd.DataFrame(
        {
            "Дата операции": [
                "31.12.2021",
                "30.12.2021",
                "29.12.2021",
            ],
            "Сумма платежа": [-100.0, -500.0, -200.0],
            "Категория": ["Супермаркеты", "Переводы", "Аптеки"],
            "Описание": ["Лента", "Иван И.", "Аптека"],
        }
    )

    result = get_top_transactions(dataframe)

    assert result[0]["amount"] == 500.0
    assert result[0]["category"] == "Переводы"
    assert result[0]["date"] == "30.12.2021"


@patch("src.views.get_stock_prices")
@patch("src.views.get_currency_rates")
@patch("src.views.load_user_settings")
def test_main_page(
    mock_settings: Any,
    mock_currency_rates: Any,
    mock_stock_prices: Any,
) -> None:
    """Тестирует JSON-ответ для страницы Главная."""
    mock_settings.return_value = {
        "user_currencies": ["USD"],
        "user_stocks": ["AAPL"],
    }
    mock_currency_rates.return_value = [
        {
            "currency": "USD",
            "rate": 90.0,
        }
    ]
    mock_stock_prices.return_value = [
        {
            "stock": "AAPL",
            "price": 150.0,
        }
    ]

    dataframe = pd.DataFrame(
        {
            "Дата операции": ["31.12.2021"],
            "Номер карты": ["*1234"],
            "Сумма платежа": [-100.0],
            "Категория": ["Супермаркеты"],
            "Описание": ["Лента"],
        }
    )

    result = json.loads(main_page("2021-12-31 16:00:00", dataframe))

    assert result["greeting"] == "Добрый день"
    assert result["cards"][0]["last_digits"] == "1234"
    assert result["top_transactions"][0]["description"] == "Лента"
    assert result["currency_rates"][0]["currency"] == "USD"
    assert result["stock_prices"][0]["stock"] == "AAPL"
