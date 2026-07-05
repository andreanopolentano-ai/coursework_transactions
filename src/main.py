from src.reports import spending_by_category
from src.services import phone_number_search, simple_search
from src.utils import load_transactions_from_excel
from src.views import main_page


def main() -> None:
    """Запускает демонстрацию работы курсового проекта."""
    transactions = load_transactions_from_excel("data/operations.xlsx")

    print("JSON-ответ для страницы Главная:")
    print(main_page("2021-12-31 16:00:00", transactions))

    print("Простой поиск:")
    print(simple_search(transactions, "супермаркет"))

    print("Поиск по телефонным номерам:")
    print(phone_number_search(transactions))

    print("Отчет по категории:")
    print(spending_by_category(transactions, "Супермаркеты", "2021-12-31"))


if __name__ == "__main__":
    main()
