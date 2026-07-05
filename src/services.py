import json
import re

import pandas as pd


CATEGORY_COLUMN = "Категория"
DESCRIPTION_COLUMN = "Описание"


def simple_search(
    transactions: pd.DataFrame,
    search_query: str,
) -> str:
    """Возвращает JSON с транзакциями, найденными по описанию или категории."""
    if transactions.empty:
        return json.dumps([], ensure_ascii=False, indent=4)

    query = search_query.lower()

    result = list(
        filter(
            lambda row: query in str(row.get(DESCRIPTION_COLUMN, "")).lower()
            or query in str(row.get(CATEGORY_COLUMN, "")).lower(),
            transactions.to_dict(orient="records"),
        )
    )

    return json.dumps(result, ensure_ascii=False, indent=4, default=str)


def phone_number_search(transactions: pd.DataFrame) -> str:
    """Возвращает JSON с транзакциями, содержащими телефонные номера."""
    if transactions.empty or DESCRIPTION_COLUMN not in transactions.columns:
        return json.dumps([], ensure_ascii=False, indent=4)

    phone_pattern = re.compile(
        r"(\+7|8)\s?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}"
    )

    result = list(
        filter(
            lambda row: bool(
                phone_pattern.search(str(row.get(DESCRIPTION_COLUMN, "")))
            ),
            transactions.to_dict(orient="records"),
        )
    )

    return json.dumps(result, ensure_ascii=False, indent=4, default=str)


def transfers_to_individuals_search(transactions: pd.DataFrame) -> str:
    """Возвращает JSON с переводами физическим лицам."""
    if transactions.empty:
        return json.dumps([], ensure_ascii=False, indent=4)

    name_pattern = re.compile(r"[А-ЯЁ][а-яё]+\s[А-ЯЁ]\.")

    result = list(
        filter(
            lambda row: str(row.get(CATEGORY_COLUMN, "")) == "Переводы"
            and bool(name_pattern.search(str(row.get(DESCRIPTION_COLUMN, "")))),
            transactions.to_dict(orient="records"),
        )
    )

    return json.dumps(result, ensure_ascii=False, indent=4, default=str)
