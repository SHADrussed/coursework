import datetime
import logging
from typing import List, Dict, Tuple

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def filter_transactions_by_month(
    transactions: List[Dict], year: int, month: int
) -> List[Dict]:
    """
    Фильтрует транзакции по заданному году и месяцу.
    Использует функциональный подход с list comprehension.
    """
    try:
        start_date = datetime.date(year, month, 1)
        # Последний день месяца
        end_date = datetime.date(year, month % 12 + 1, 1) - datetime.timedelta(days=1)
        return [
            tran for tran in transactions
            if start_date <= datetime.datetime.strptime(tran['Дата операции'], "%d.%m.%Y").date() <= end_date
        ]
    except (ValueError, KeyError) as e:
        logger.error(f"Ошибка при фильтрации транзакций: {e}")
        return []

def calculate_category_benefits(
    transactions: List[Dict], standard_rate: float = 0.01, increased_rate: float = 0.05
) -> Dict[str, float]:
    """
    Вычисляет выгоду от повышенного кешбэка для каждой категории.
    Использует reduce-подобный подход через словарь.
    """
    # Группировка сумм по категориям с использованием словаря
    category_totals = {}
    for tran in transactions:
        category = tran['Категория']
        amount = -tran['Сумма платежа']  # Отрицательные суммы — расходы
        category_totals[category] = category_totals.get(category, 0) + amount

    # Вычисление выгоды для каждой категории
    return {
        category: total * (increased_rate - standard_rate)
        for category, total in category_totals.items()
    }

def analyze_cashback_categories(
    transactions: List[Dict], year: int, month: int
) -> List[Tuple[str, float]]:
    """
    Анализирует, какие категории были бы наиболее выгодными для повышенного кешбэка.
    Возвращает отсортированный список кортежей (категория, выгода).
    """
    try:
        # Фильтрация транзакций
        filtered_transactions = filter_transactions_by_month(transactions, year, month)
        logger.info(f"Отфильтровано {len(filtered_transactions)} транзакций за {year}-{month:02d}")

        if not filtered_transactions:
            logger.warning("Нет транзакций за указанный период")
            return []

        # Вычисление выгоды по категориям
        benefits = calculate_category_benefits(filtered_transactions)

        # Сортировка категорий по убыванию выгоды с использованием sorted и lambda
        sorted_categories = sorted(
            benefits.items(),
            key=lambda x: x[1],
            reverse=True
        )

        logger.info(f"Топ категория: {sorted_categories[0][0]} с выгодой {sorted_categories[0][1]:.2f}")
        return sorted_categories

    except Exception as e:
        logger.error(f"Ошибка в анализе категорий: {e}")
        return []