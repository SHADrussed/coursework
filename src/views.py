import datetime
import json
import os

import requests
from src.transaction_reader import read_transactions_from_excel

from dotenv import load_dotenv
load_dotenv()

# Load user settings once (assuming user_settings.json is in the project root)
with open('../data/user_settings.json', 'r', encoding='utf-8') as f:
    user_settings = json.load(f)


# Greeting function
def get_greet(date_n_time):
    """Return a greeting based on the hour of the day."""
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


# Card summary function
def get_cards(data, closing_date):
    """Summarize card spending and cashback from transactions."""
    cards_dict = {}
    start_date = closing_date.replace(day=1)

    for tran in data:
        # Skip if 'Дата платежа' is empty, or status is not 'OK'
        if not tran['Дата платежа'] or tran['Статус'] != 'OK':
            continue
        try:
            tran_date = datetime.datetime.strptime(str(tran['Дата платежа']), "%d.%m.%Y")
        except ValueError:
            continue  # Skip if date format is invalid
        if start_date <= tran_date <= closing_date:
            amount = tran['Сумма платежа']
            if amount >= 0:  # Skip income transactions
                continue
            amount = -amount  # Convert expenses to positive
            card_number = str(tran['Номер карты']).strip()
            if card_number and card_number != 'nan':
                last_digits = card_number[-4:]
                if last_digits not in cards_dict:
                    cards_dict[last_digits] = {'total_spent': 0, 'cashback': 0}
                cards_dict[last_digits]['total_spent'] += amount
                cards_dict[last_digits]['cashback'] += amount * 0.01  # 1% cashback

    return [
        {'last_digits': digits, 'total_spent': info['total_spent'], 'cashback': info['cashback']}
        for digits, info in cards_dict.items()
    ]


# Top transactions function
def get_top_transactions(data, closing_date):
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


# Currency rates function (example API)
def get_currency_rates(currencies):
    """Fetch currency exchange rates from an API."""
    try:
        # Using a free API example (replace with your chosen API)
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
        print(f"Error fetching currency rates: {e}")
        return []


# Stock prices function (example Hawkins example API)
def get_stock_prices(stocks):
    """Fetch stock prices from an API."""
    try:
        # Using Alpha Vantage as an example (requires API key in .env)
        api_key = os.getenv("STOCK_API")  # Load from .env in production
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
        print(f"Error fetching stock prices: {e}")
        return []


# Main function
def main_page(date_n_time, user_data=None):
    """Generate JSON response for the main page."""
    if user_data is None:
        user_data = read_transactions_from_excel(r"D:\PythonProjects\Bank_Homework\data\operations.xlsx")

    closing_date = datetime.datetime.strptime(date_n_time.split()[0], "%Y-%m-%d")

    response = {
        'greeting': get_greet(date_n_time),
        'cards': get_cards(user_data, closing_date),
        'top_transactions': get_top_transactions(user_data, closing_date),
        'currency_rates': get_currency_rates(user_settings['user_currencies']),
        'stock_prices': get_stock_prices(user_settings['user_stocks'])
    }
    return response


result = main_page('2018-04-02 12:00:01')
print(json.dumps(result, ensure_ascii=False, indent=2))