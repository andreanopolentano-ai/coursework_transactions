import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd
import requests


LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

utils_logger = logging.getLogger(__name__)
utils_logger.setLevel(logging.DEBUG)
utils_logger.propagate = False

if not utils_logger.handlers:
    utils_file_handler = logging.FileHandler(
        LOGS_DIR / "utils.log",
        mode="w",
        encoding="utf-8",
    )
    utils_file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    utils_file_handler.setFormatter(utils_file_formatter)
    utils_logger.addHandler(utils_file_handler)


def load_transactions_from_json(file_path: str) -> list[dict[str, Any]]:
    """Возвращает список транзакций из JSON-файла."""
    path = Path(file_path)

    utils_logger.debug("Start reading JSON file: %s", file_path)

    try:
        with path.open(encoding="utf-8") as file:
            transactions = json.load(file)
    except FileNotFoundError as error:
        utils_logger.error("JSON file was not found: %s", error)
        return []
    except json.JSONDecodeError as error:
        utils_logger.error("JSON file decoding error: %s", error)
        return []

    if not isinstance(transactions, list):
        utils_logger.error("JSON file does not contain a list: %s", file_path)
        return []

    utils_logger.info(
        "JSON file was loaded successfully. Transactions count: %s",
        len(transactions),
    )

    return transactions


def load_transactions_from_excel(file_path: str) -> pd.DataFrame:
    """Возвращает датафрейм с транзакциями из Excel-файла."""
    path = Path(file_path)

    try:
        dataframe = pd.read_excel(path)
    except FileNotFoundError as error:
        utils_logger.error("Excel file was not found: %s", error)
        return pd.DataFrame()
    except ValueError as error:
        utils_logger.error("Excel file reading error: %s", error)
        return pd.DataFrame()

    utils_logger.info(
        "Excel file was loaded successfully. Rows count: %s",
        len(dataframe),
    )

    return dataframe


def load_user_settings(file_path: str = "user_settings.json") -> dict[str, Any]:
    """Возвращает пользовательские настройки из JSON-файла."""
    path = Path(file_path)

    try:
        with path.open(encoding="utf-8") as file:
            settings = json.load(file)
    except FileNotFoundError as error:
        utils_logger.error("Settings file was not found: %s", error)
        return {"user_currencies": [], "user_stocks": []}
    except json.JSONDecodeError as error:
        utils_logger.error("Settings file decoding error: %s", error)
        return {"user_currencies": [], "user_stocks": []}

    if not isinstance(settings, dict):
        return {"user_currencies": [], "user_stocks": []}

    return settings


def get_currency_rates(currencies: list[str]) -> list[dict[str, float | str]]:
    """Возвращает курсы валют к рублю."""
    result = []

    for currency in currencies:
        rate = 1.0

        try:
            response = requests.get(
                f"https://api.exchangerate-api.com/v4/latest/{currency}",
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            rate = float(data.get("rates", {}).get("RUB", 1.0))
        except requests.RequestException as error:
            utils_logger.error("Currency API error for %s: %s", currency, error)
        except (TypeError, ValueError) as error:
            utils_logger.error("Currency data error for %s: %s", currency, error)

        if rate <= 0:
            rate = 1.0

        result.append(
            {
                "currency": currency,
                "rate": round(float(rate), 2),
            }
        )

    return result


def get_stock_prices(stocks: list[str]) -> list[dict[str, float | str]]:
    """Возвращает цены акций."""
    result = []

    for stock in stocks:
        price = 1.0

        try:
            response = requests.get(
                f"https://query1.finance.yahoo.com/v8/finance/chart/{stock}",
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            meta = data["chart"]["result"][0]["meta"]
            price = float(meta.get("regularMarketPrice", 1.0))
        except requests.RequestException as error:
            utils_logger.error("Stock API error for %s: %s", stock, error)
        except (KeyError, IndexError, TypeError, ValueError) as error:
            utils_logger.error("Stock data error for %s: %s", stock, error)

        if price <= 0:
            price = 1.0

        result.append(
            {
                "stock": stock,
                "price": round(float(price), 2),
            }
        )

    return result
