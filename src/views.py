import json
from datetime import datetime
from typing import Any

import pandas as pd

from src.utils import (
    get_currency_rates,
    get_stock_prices,
    load_transactions_from_excel,
    load_user_settings,
)


DATE_COLUMN = "Дата операции"
CARD_COLUMN = "Номер карты"
AMOUNT_COLUMN = "Сумма платежа"
CATEGORY_COLUMN = "Категория"
DESCRIPTION_COLUMN = "Описание"


def main_page(
    date_time: str,
    transactions: pd.DataFrame | None = None,
) -> str:
    """Возвращает JSON-ответ для страницы Главная."""
    current_datetime = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")

    if transactions is None:
        transactions = load_transactions_from_excel("data/operations.xlsx")

    filtered_transactions = _filter_transactions_by_month(
        transactions,
        current_datetime,
    )

    settings = load_user_settings()

    response = {
        "greeting": get_greeting(current_datetime),
        "cards": get_cards_info(filtered_transactions),
        "top_transactions": get_top_transactions(filtered_transactions),
        "currency_rates": get_currency_rates(
            settings.get("user_currencies", [])
        ),
        "stock_prices": get_stock_prices(settings.get("user_stocks", [])),
    }

    return json.dumps(response, ensure_ascii=False, indent=4)


def get_greeting(current_datetime: datetime) -> str:
    """Возвращает приветствие в зависимости от времени."""
    hour = current_datetime.hour

    if 6 <= hour <= 11:
        return "Доброе утро"
    if 12 <= hour <= 17:
        return "Добрый день"
    if 18 <= hour <= 22:
        return "Добрый вечер"

    return "Доброй ночи"


def get_cards_info(transactions: pd.DataFrame) -> list[dict[str, Any]]:
    """Возвращает информацию по банковским картам."""
    required_columns = {CARD_COLUMN, AMOUNT_COLUMN}

    if transactions.empty or not required_columns.issubset(transactions.columns):
        return []

    expenses = transactions[transactions[AMOUNT_COLUMN] < 0].copy()
    expenses[AMOUNT_COLUMN] = expenses[AMOUNT_COLUMN].abs()

    grouped_cards = (
        expenses.groupby(CARD_COLUMN)[AMOUNT_COLUMN]
        .sum()
        .reset_index()
        .sort_values(AMOUNT_COLUMN, ascending=False)
    )

    cards = []

    for _, row in grouped_cards.iterrows():
        total_spent = round(float(row[AMOUNT_COLUMN]), 2)

        cards.append(
            {
                "last_digits": str(row[CARD_COLUMN])[-4:],
                "total_spent": total_spent,
                "cashback": round(total_spent / 100, 2),
            }
        )

    return cards


def get_top_transactions(transactions: pd.DataFrame) -> list[dict[str, Any]]:
    """Возвращает топ-5 транзакций по сумме платежа."""
    required_columns = {
        DATE_COLUMN,
        AMOUNT_COLUMN,
        CATEGORY_COLUMN,
        DESCRIPTION_COLUMN,
    }

    if transactions.empty or not required_columns.issubset(transactions.columns):
        return []

    top_transactions = transactions.copy()
    top_transactions["amount_for_sort"] = top_transactions[AMOUNT_COLUMN].abs()

    top_transactions = top_transactions.sort_values(
        "amount_for_sort",
        ascending=False,
    ).head(5)

    result = []

    for _, row in top_transactions.iterrows():
        operation_date = pd.to_datetime(row[DATE_COLUMN], dayfirst=True)

        result.append(
            {
                "date": operation_date.strftime("%d.%m.%Y"),
                "amount": round(float(abs(row[AMOUNT_COLUMN])), 2),
                "category": str(row[CATEGORY_COLUMN]),
                "description": str(row[DESCRIPTION_COLUMN]),
            }
        )

    return result


def _filter_transactions_by_month(
    transactions: pd.DataFrame,
    current_datetime: datetime,
) -> pd.DataFrame:
    """Возвращает транзакции с начала месяца по указанную дату."""
    if transactions.empty or DATE_COLUMN not in transactions.columns:
        return pd.DataFrame()

    filtered_transactions = transactions.copy()
    filtered_transactions[DATE_COLUMN] = pd.to_datetime(
        filtered_transactions[DATE_COLUMN],
        dayfirst=True,
        errors="coerce",
    )

    start_date = current_datetime.replace(
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    end_date = current_datetime

    return filtered_transactions[
        (filtered_transactions[DATE_COLUMN] >= start_date)
        & (filtered_transactions[DATE_COLUMN] <= end_date)
    ]
