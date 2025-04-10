import datetime
import json
import os
from typing import List, Dict

import requests
from src.transaction_reader import read_transactions_from_excel
from dotenv import load_dotenv

load_dotenv()

# Определение директории данных относительно текущего файла
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

# Загрузка настроек пользователя из файла user_settings.json в директории data
with open(os.path.join(DATA_DIR, 'user_settings.json'), 'r', encoding='utf-8') as f:
    user_settings = json.load(f)


# Функция для приветствия на основе времени суток
def get_greet(date_n_time: str) -> str:
    """
    Возвращает приветствие на основе часа дня.

    Args:
        date_n_time (str): Дата и время в формате '%Y-%m-%d %H:%M:%S'.

    Returns:
        str: Приветствие.
    """
    date_obj = datetime.datetime.strptime(date_n_time, "%Y-%m-%d %H:%M:%S")
    hour = date_obj.hour
    if 4 <= hour < 12:
        return 'Доброе утро'
    elif 12 <= hour < 18:
        return 'Добрый день'
    elif 18 <= hour < 21:
        return 'Добрый вечер'
    else:
        return 'Доброй ночи'


# Функция для подведения итогов по картам
def get_cards(data: List[Dict], closing_date: datetime.datetime) -> List[Dict]:
    """
    Подводит итоги по тратам и кешбэку по картам из транзакций.

    Args:
        data (List[Dict]): Список транзакций.
        closing_date (datetime.datetime): Дата закрытия периода.

    Returns:
        List[Dict]: Список словарей с итогами по картам.
    """
    cards_dict = {}
    start_date = closing_date.replace(day=1)

    for tran in data:
        # Пропускаем, если 'Дата платежа' пустая или статус не 'OK'
        if not tran['Дата платежа'] or tran['Статус'] != 'OK':
            continue
        try:
            tran_date = datetime.datetime.strptime(str(tran['Дата платежа']), "%d.%m.%Y")
        except ValueError:
            continue  # Пропускаем, если формат даты неверный
        if start_date <= tran_date <= closing_date:
            amount = tran['Сумма платежа']
            if amount >= 0:  # Пропускаем доходные транзакции
                continue
            amount = -amount  # Преобразуем расходы в положительное число
            card_number = str(tran['Номер карты']).strip()
            if card_number and card_number != 'nan':
                last_digits = card_number[-4:]
                if last_digits not in cards_dict:
                    cards_dict[last_digits] = {'total_spent': 0, 'cashback': 0}
                cards_dict[last_digits]['total_spent'] += amount
                cards_dict[last_digits]['cashback'] += amount * 0.01  # 1% кешбэк

    return [
        {'last_digits': digits, 'total_spent': info['total_spent'], 'cashback': info['cashback']}
        for digits, info in cards_dict.items()
    ]


# Функция для получения топ-5 транзакций
def get_top_transactions(data: List[Dict], closing_date: datetime.datetime) -> List[Dict]:
    """
    Возвращает топ-5 транзакций по сумме за период.

    Args:
        data (List[Dict]): Список транзакций.
        closing_date (datetime.datetime): Дата закрытия периода.

    Returns:
        List[Dict]: Список топ-5 транзакций.
    """
    start_date = closing_date.replace(day=1)
    transactions = [
        {
            'date': tran['Дата платежа'],
            'amount': tran['Сумма платежа'],
            'category': tran['Категория'],
            'description': tran['Описание']
        }
        for tran in data
        if isinstance(tran['Дата платежа'], str) and tran['Дата платежа'] and tran['Статус'] == 'OK'
           and start_date <= datetime.datetime.strptime(tran['Дата платежа'], "%d.%m.%Y") <= closing_date
    ]
    return sorted(transactions, key=lambda x: abs(x['amount']), reverse=True)[:5]


# Функция для получения курсов валют
def get_currency_rates(currencies: List[str]) -> List[Dict]:
    """
    Получает курсы обмена валют через API.

    Args:
        currencies (List[str]): Список валют для запроса.

    Returns:
        List[Dict]: Список словарей с курсами валют.
    """
    try:
        # Используем бесплатный API (замените на нужный)
        url = 'https://api.exchangerate-api.com/v4/latest/RUB'
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        rates = [
            {'currency': currency, 'rate': data['rates'][currency]}
            for currency in currencies if currency in data['rates']
        ]
        return rates
    except requests.RequestException as e:
        print(f"Ошибка получения курсов валют: {e}")
        return []


# Функция для получения цен акций
def get_stock_prices(stocks: List[str]) -> List[Dict]:
    """
    Получает цены акций через API.

    Args:
        stocks (List[str]): Список тикеров акций.

    Returns:
        List[Dict]: Список словарей с ценами акций.
    """
    try:
        # Используем Alpha Vantage (требуется API ключ в .env)
        api_key = os.getenv("STOCK_API")
        url = 'https://www.alphavantage.co/query'
        prices = []
        for stock in stocks:
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': stock,
                'apikey': api_key
            }
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            if 'Global Quote' in data and '05. price' in data['Global Quote']:
                prices.append({
                    'stock': stock,
                    'price': float(data['Global Quote']['05. price'])
                })
        return prices
    except requests.RequestException as e:
        print(f"Ошибка получения цен акций: {e}")
        return []


# Основная функция для генерации JSON-ответа
def main_page(date_n_time: str, user_data: Optional[List[Dict]] = None) -> Dict:
    """
    Генерирует JSON-ответ для главной страницы.

    Args:
        date_n_time (str): Дата и время в формате '%Y-%m-%d %H:%M:%S'.
        user_data (Optional[List[Dict]]): Данные транзакций, если не None.

    Returns:
        Dict: JSON-ответ с данными.
    """
    if user_data is None:
        user_data_path = os.path.join(DATA_DIR, 'operations.xlsx')
        user_data = read_transactions_from_excel(user_data_path)

    closing_date = datetime.datetime.strptime(date_n_time.split()[0], "%Y-%m-%d")

    response = {
        'greeting': get_greet(date_n_time),
        'cards': get_cards(user_data, closing_date),
        'top_transactions': get_top_transactions(user_data, closing_date),
        'currency_rates': get_currency_rates(user_settings['user_currencies']),
        'stock_prices': get_stock_prices(user_settings['user_stocks'])
    }
    return response


if __name__ == "__main__":
    result = main_page('2018-04-02 12:00:01')
    print(json.dumps(result, ensure_ascii=False, indent=2))