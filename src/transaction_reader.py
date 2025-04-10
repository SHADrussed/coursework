import csv
import pandas as pd
from typing import List, Dict


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


def read_transactions_from_excel(file_path: str) -> List[Dict[str, any]]:
    """
    Считывает транзакции из Excel-файла и возвращает список словарей.

    Args:
        file_path (str): Путь к Excel-файлу.

    Returns:
        List[Dict[str, any]]: Список транзакций.
    """
    df = pd.read_excel(file_path)
    return df.to_dict("records")