import csv
import logging
import pandas as pd
from typing import List, Dict

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def read_transactions_from_excel(file_path: str) -> List[Dict[str, any]]:
    """
    Считывает транзакции из Excel-файла и возвращает список словарей.

    Args:
        file_path (str): Путь к Excel-файлу.

    Returns:
        List[Dict[str, any]]: Список транзакций.
    """
    df = pd.read_excel(file_path)
    # Преобразуем 'Дата операции' в datetime с указанием формата
    df['Дата операции'] = pd.to_datetime(df['Дата операции'], format='%d.%m.%Y %H:%M:%S', errors='coerce')
    # Преобразуем 'Дата платежа' в datetime с указанием формата
    df['Дата платежа'] = pd.to_datetime(df['Дата платежа'], format='%d.%m.%Y', errors='coerce')

    # Логирование некорректных дат
    invalid_ops = df[df['Дата операции'].isnull()]
    if not invalid_ops.empty:
        logger.warning(f"Некорректные 'Дата операции' в строках: {invalid_ops.index.tolist()}")

    invalid_pays = df[df['Дата платежа'].isnull()]
    if not invalid_pays.empty:
        logger.warning(f"Некорректные 'Дата платежа' в строках: {invalid_pays.index.tolist()}")

    return df.to_dict("records")

def read_transactions_from_csv(path: str) -> List[Dict[str, str]]:
    """
    Считывает транзакции из CSV-файла и возвращает список словарей.

    Args:
        path (str): Путь к CSV-файлу.

    Returns:
        List[Dict[str, str]]: Список транзакций.
    """
    with open(path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)