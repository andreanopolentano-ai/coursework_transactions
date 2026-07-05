import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pandas as pd
import requests

from src.utils import (
    get_currency_rates,
    get_stock_prices,
    load_transactions_from_excel,
    load_user_settings,
)


class MockResponse:
    """Тестовый ответ API."""

    def __init__(self, data: dict[str, Any]) -> None:
        """Инициализирует тестовый ответ."""
        self.data = data

    def raise_for_status(self) -> None:
        """Имитирует успешный HTTP-ответ."""

    def json(self) -> dict[str, Any]:
        """Возвращает JSON-данные."""
        return self.data


def test_load_transactions_from_excel(tmp_path: Path) -> None:
    """Тестирует чтение транзакций из Excel-файла."""
    file_path = tmp_path / "operations.xlsx"
    dataframe = pd.DataFrame(
        {
            "Дата операции": ["2021-12-01"],
            "Сумма платежа": [-100],
            "Категория": ["Супермаркеты"],
        }
    )
    dataframe.to_excel(file_path, index=False)

    result = load_transactions_from_excel(str(file_path))

    assert len(result) == 1
    assert result.loc[0, "Категория"] == "Супермаркеты"


def test_load_transactions_from_excel_not_found() -> None:
    """Тестирует чтение отсутствующего Excel-файла."""
    result = load_transactions_from_excel("wrong_file.xlsx")

    assert result.empty


def test_load_user_settings(tmp_path: Path) -> None:
    """Тестирует чтение пользовательских настроек."""
    file_path = tmp_path / "user_settings.json"
    settings = {
        "user_currencies": ["USD", "EUR"],
        "user_stocks": ["AAPL"],
    }

    file_path.write_text(
        json.dumps(settings, ensure_ascii=False),
        encoding="utf-8",
    )

    result = load_user_settings(str(file_path))

    assert result == settings


def test_load_user_settings_not_found() -> None:
    """Тестирует чтение отсутствующего файла настроек."""
    result = load_user_settings("wrong_settings.json")

    assert result == {
        "user_currencies": [],
        "user_stocks": [],
    }


@patch("src.utils.requests.get")
def test_get_currency_rates(mock_get: Any) -> None:
    """Тестирует получение курсов валют."""
    mock_get.return_value = MockResponse(
        {
            "rates": {
                "RUB": 90.55,
            }
        }
    )

    result = get_currency_rates(["USD"])

    assert result == [
        {
            "currency": "USD",
            "rate": 90.55,
        }
    ]


@patch("src.utils.requests.get")
def test_get_currency_rates_api_error(mock_get: Any) -> None:
    """Тестирует обработку ошибки API валют."""
    mock_get.side_effect = requests.RequestException

    result = get_currency_rates(["USD"])

    assert result == [
        {
            "currency": "USD",
            "rate": 1.0,
        }
    ]


@patch("src.utils.requests.get")
def test_get_stock_prices(mock_get: Any) -> None:
    """Тестирует получение стоимости акций."""
    mock_get.return_value = MockResponse(
        {
            "chart": {
                "result": [
                    {
                        "meta": {
                            "regularMarketPrice": 150.12,
                        }
                    }
                ]
            }
        }
    )

    result = get_stock_prices(["AAPL"])

    assert result == [
        {
            "stock": "AAPL",
            "price": 150.12,
        }
    ]


@patch("src.utils.requests.get")
def test_get_stock_prices_api_error(mock_get: Any) -> None:
    """Тестирует обработку ошибки API акций."""
    mock_get.side_effect = requests.RequestException

    result = get_stock_prices(["AAPL"])

    assert result == [
        {
            "stock": "AAPL",
            "price": 1.0,
        }
    ]
