import pytest
from src.services import analyze_cashback_categories

def test_analyze_cashback_categories():
    """
    Тестирует функцию analyze_cashback_categories с примером транзакций.
    """
    sample_transactions = [
        {"Дата операции": "01.04.2025", "Сумма платежа": -100, "Категория": "Еда"},
        {"Дата операции": "15.04.2025", "Сумма платежа": -200, "Категория": "Транспорт"}
    ]
    result = analyze_cashback_categories(sample_transactions, 2025, 4)
    assert len(result) == 2
    assert result[0][0] == "Транспорт"  # Большие траты => больше выгоды
    assert result[0][1] == 8.0  # (200 * (0.05 - 0.01))

def test_empty_transactions():
    """
    Тестирует функцию analyze_cashback_categories с пустым списком транзакций.
    """
    result = analyze_cashback_categories([], 2025, 4)
    assert result == []

def test_invalid_date():
    """
    Тестирует функцию analyze_cashback_categories с неверной датой.
    """
    sample_transactions = [{"Дата операции": "invalid", "Сумма платежа": -100, "Категория": "Еда"}]
    result = analyze_cashback_categories(sample_transactions, 2025, 4)
    assert result == []