import logging
import os
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional

import pandas as pd

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Декоратор для записи результата в файл
def log_to_file(filename: Optional[str] = None):
    """
    Декоратор для записи результата функции в файл.
    Если filename не указан, используется имя по умолчанию: report_YYYYMMDD_HHMMSS.csv.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            # Определяем имя файла
            output_file = filename if filename else f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            try:
                result.to_csv(output_file, index=False)
                logger.info(f"Отчет сохранен в файл: {output_file}")
            except Exception as e:
                logger.error(f"Ошибка при сохранении отчета в файл {output_file}: {e}")
            return result

        return wrapper

    return decorator


# Функция для получения трат по категории
@log_to_file()  # Используем декоратор без параметра (имя файла по умолчанию)
def spending_by_category(
        transactions: pd.DataFrame,
        category: str,
        date: Optional[str] = None
) -> pd.DataFrame:
    """
    Возвращает траты по заданной категории за последние три месяца от указанной даты.

    Аргументы:
        transactions (pd.DataFrame): Датафрейм с транзакциями.
        category (str): Название категории для фильтрации.
        date (Optional[str]): Дата в формате 'YYYY-MM-DD'. Если None, используется текущая дата.

    Возвращает:
        pd.DataFrame: Отфильтрованные траты по категории.
    """
    try:
        # Определяем конечную дату (текущая, если не указана)
        end_date = datetime.now() if date is None else datetime.strptime(date, "%Y-%m-%d")

        # Вычисляем начальную дату (три месяца назад)
        start_date = end_date - timedelta(days=90)

        # Преобразуем столбец 'Дата операции' в datetime, если он еще не в этом формате
        if not pd.api.types.is_datetime64_any_dtype(transactions['Дата операции']):
            transactions['Дата операции'] = pd.to_datetime(transactions['Дата операции'])

        # Фильтруем транзакции по дате и категории
        filtered_transactions = transactions[
            (transactions['Дата операции'].dt.date >= start_date.date()) &
            (transactions['Дата операции'].dt.date <= end_date.date()) &
            (transactions['Категория'] == category)
            ]

        # Возвращаем только траты (отрицательные суммы)
        spending = filtered_transactions[filtered_transactions['Сумма платежа'] < 0]

        logger.info(f"Отчет по категории '{category}' за период с {start_date.date()} по {end_date.date()} сформирован")
        return spending

    except ValueError as e:
        logger.error(f"Ошибка формата даты: {e}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Ошибка при формировании отчета: {e}")
        return pd.DataFrame()


# Пример использования
if __name__ == "__main__":
    # Пример датафрейма
    data = {
        'Дата операции': ['2025-01-15', '2025-02-20', '2025-03-10', '2025-04-01'],
        'Сумма платежа': [-100, -200, -150, -50],
        'Категория': ['Еда', 'Транспорт', 'Еда', 'Еда']
    }
    df = pd.DataFrame(data)

    # Вызов с указанием даты
    report = spending_by_category(df, 'Еда', '2025-04-02')
    print("Отчет с указанной датой:")
    print(report)

    # Вызов без даты
    report_current = spending_by_category(df, 'Транспорт')
    print("\nОтчет с текущей датой:")
    print(report_current)