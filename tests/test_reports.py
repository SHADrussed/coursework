import pandas as pd
import pytest
from src.reports import spending_by_category

def test_spending_by_category_with_date():
    data = {
        'Дата операции': ['2025-01-15', '2025-02-20', '2025-03-10', '2025-04-01'],
        'Сумма платежа': [-100, -200, -150, -50],
        'Категория': ['Еда', 'Транспорт', 'Еда', 'Еда']
    }
    df = pd.DataFrame(data)
    result = spending_by_category(df, 'Еда', '2025-04-02')
    assert len(result) == 3  # Три траты по категории "Еда"
    assert result['Сумма платежа'].sum() == -300  # -100 + -150 + -50

def test_spending_by_category_no_date():
    data = {
        'Дата операции': ['2025-01-15', '2025-02-20'],
        'Сумма платежа': [-100, -200],
        'Категория': ['Еда', 'Транспорт']
    }
    df = pd.DataFrame(data)
    result = spending_by_category(df, 'Транспорт')
    # Проверяем, что результат зависит от текущей даты; здесь условно
    assert 'Транспорт' in result['Категория'].values

def test_spending_by_category_invalid_date():
    data = {
        'Дата операции': ['2025-01-15'],
        'Сумма платежа': [-100],
        'Категория': ['Еда']
    }
    df = pd.DataFrame(data)
    result = spending_by_category(df, 'Еда', 'invalid_date')
    assert result.empty  # Пустой датафрейм при неверной дате