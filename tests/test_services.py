import json

import pandas as pd

from src.services import (
    phone_number_search,
    simple_search,
    transfers_to_individuals_search,
)


def test_simple_search_by_description() -> None:
    """Тестирует простой поиск по описанию."""
    dataframe = pd.DataFrame(
        {
            "Категория": ["Супермаркеты", "Аптеки"],
            "Описание": ["Лента", "Горздрав"],
        }
    )

    result = json.loads(simple_search(dataframe, "лента"))

    assert len(result) == 1
    assert result[0]["Описание"] == "Лента"


def test_simple_search_by_category() -> None:
    """Тестирует простой поиск по категории."""
    dataframe = pd.DataFrame(
        {
            "Категория": ["Супермаркеты", "Аптеки"],
            "Описание": ["Лента", "Горздрав"],
        }
    )

    result = json.loads(simple_search(dataframe, "аптеки"))

    assert len(result) == 1
    assert result[0]["Категория"] == "Аптеки"


def test_phone_number_search() -> None:
    """Тестирует поиск транзакций с телефонными номерами."""
    dataframe = pd.DataFrame(
        {
            "Категория": ["Мобильная связь", "Супермаркеты"],
            "Описание": ["МТС +7 921 111-22-33", "Лента"],
        }
    )

    result = json.loads(phone_number_search(dataframe))

    assert len(result) == 1
    assert result[0]["Описание"] == "МТС +7 921 111-22-33"


def test_phone_number_search_with_eight() -> None:
    """Тестирует поиск номера в формате 89000000000."""
    dataframe = pd.DataFrame(
        {
            "Категория": ["Мобильная связь", "Супермаркеты"],
            "Описание": ["Оплата 89000000000", "Лента"],
        }
    )

    result = json.loads(phone_number_search(dataframe))

    assert len(result) == 1
    assert result[0]["Описание"] == "Оплата 89000000000"


def test_transfers_to_individuals_search() -> None:
    """Тестирует поиск переводов физическим лицам."""
    dataframe = pd.DataFrame(
        {
            "Категория": ["Переводы", "Переводы", "Супермаркеты"],
            "Описание": ["Валерий А.", "Оплата услуг", "Лента"],
        }
    )

    result = json.loads(transfers_to_individuals_search(dataframe))

    assert len(result) == 1
    assert result[0]["Описание"] == "Валерий А."
