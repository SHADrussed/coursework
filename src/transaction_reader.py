import csv

import pandas as pd


def read_transactions_from_csv(path):
    """Считывает транзакции из CSV-файла и возвращает список словарей."""
    with open(path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)


def read_transactions_from_excel(file_path):
    """Считывает транзакции из Excel-файла и возвращает список словарей."""
    df = pd.read_excel(file_path)
    return df.to_dict("records")

#
# csv_data = read_transactions_from_csv(r"D:\PythonProjects\Bank_Homework\data\transactions.csv")
#excel_data = read_transactions_from_excel(r"D:\PythonProjects\Bank_Homework\data\operations.xlsx")
#
# print(csv_data)
#print(excel_data)