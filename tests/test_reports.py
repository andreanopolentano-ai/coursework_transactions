from pathlib import Path

import pandas as pd

import src.reports as reports
from src.reports import spending_by_category


def test_spending_by_category(tmp_path: Path) -> None:
    """Тестирует отчет по тратам за категорию."""
    reports.REPORTS_DIR = tmp_path

    dataframe = pd.DataFrame(
        {
            "Дата операции": [
                "31.12.2021",
                "01.12.2021",
                "01.06.2021",
            ],
            "Категория": [
                "Супермаркеты",
                "Супермаркеты",
                "Супермаркеты",
            ],
            "Сумма платежа": [
                -100.0,
                -200.0,
                -300.0,
            ],
        }
    )

    result = spending_by_category(
        dataframe,
        "Супермаркеты",
        "2021-12-31",
    )

    assert len(result) == 2
    assert result["Сумма платежа"].sum() == 300.0
    assert (tmp_path / "spending_by_category_report.json").exists()


def test_spending_by_category_empty_dataframe(tmp_path: Path) -> None:
    """Тестирует отчет при пустом датафрейме."""
    reports.REPORTS_DIR = tmp_path

    result = spending_by_category(
        pd.DataFrame(),
        "Супермаркеты",
        "2021-12-31",
    )

    assert result.empty
    assert (tmp_path / "spending_by_category_report.json").exists()
