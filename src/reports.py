import json
from collections.abc import Callable
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any

import pandas as pd


DATE_COLUMN = "Дата операции"
CATEGORY_COLUMN = "Категория"
AMOUNT_COLUMN = "Сумма платежа"

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"
REPORTS_DIR.mkdir(exist_ok=True)


def report_to_file(
    filename: str | None = None,
) -> Callable[[Callable[..., pd.DataFrame]], Callable[..., pd.DataFrame]]:
    """Записывает результат функции-отчета в файл."""

    def decorator(
        func: Callable[..., pd.DataFrame],
    ) -> Callable[..., pd.DataFrame]:
        """Оборачивает функцию отчета."""

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> pd.DataFrame:
            """Выполняет функцию и сохраняет результат в файл."""
            result = func(*args, **kwargs)

            report_filename = filename or f"{func.__name__}_report.json"
            report_path = REPORTS_DIR / report_filename

            report_data = result.to_dict(orient="records")

            with report_path.open("w", encoding="utf-8") as file:
                json.dump(report_data, file, ensure_ascii=False, indent=4, default=str)

            return result

        return wrapper

    return decorator


@report_to_file()
def spending_by_category(
    transactions: pd.DataFrame,
    category: str,
    date: str | None = None,
) -> pd.DataFrame:
    """Возвращает траты по заданной категории за последние три месяца."""
    if transactions.empty:
        return pd.DataFrame()

    required_columns = {DATE_COLUMN, CATEGORY_COLUMN, AMOUNT_COLUMN}

    if not required_columns.issubset(transactions.columns):
        return pd.DataFrame()

    current_date = _get_current_date(date)

    filtered_transactions = transactions.copy()
    filtered_transactions[DATE_COLUMN] = pd.to_datetime(
        filtered_transactions[DATE_COLUMN],
        dayfirst=True,
        errors="coerce",
    )

    start_date = current_date - pd.DateOffset(months=3)

    filtered_transactions = filtered_transactions[
        (filtered_transactions[DATE_COLUMN] >= start_date)
        & (filtered_transactions[DATE_COLUMN] <= current_date)
        & (filtered_transactions[CATEGORY_COLUMN] == category)
        & (filtered_transactions[AMOUNT_COLUMN] < 0)
    ].copy()

    filtered_transactions[AMOUNT_COLUMN] = (
        filtered_transactions[AMOUNT_COLUMN].abs()
    )

    return filtered_transactions[
        [DATE_COLUMN, CATEGORY_COLUMN, AMOUNT_COLUMN]
    ].reset_index(drop=True)


def _get_current_date(date: str | None = None) -> pd.Timestamp:
    """Возвращает дату для отчета."""
    if date is None:
        return pd.Timestamp(datetime.now())

    return pd.Timestamp(datetime.strptime(date, "%Y-%m-%d"))
