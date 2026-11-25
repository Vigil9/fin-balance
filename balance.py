"""Модуль підрахунку балансу за місяць (user story WX5-1).

Як користувач застосунку домашніх фінансів, я хочу бачити баланс
за обраний місяць (доходи мінус витрати), щоб розуміти,
чи вклався я в бюджет.
"""
from datetime import date
from decimal import Decimal

INCOME = "income"
EXPENSE = "expense"


def _parse(transaction):
    """Перевіряє одну транзакцію й повертає (дата, тип, сума)."""
    try:
        tx_date = transaction["date"]
        tx_type = transaction["type"]
        amount = transaction["amount"]
    except (KeyError, TypeError):
        raise ValueError("Транзакція має містити поля date, type, amount")

    if not isinstance(tx_date, date):
        raise ValueError("Поле date має бути об'єктом datetime.date")
    if tx_type not in (INCOME, EXPENSE):
        raise ValueError(f"Невідомий тип транзакції: {tx_type!r}")
    if isinstance(amount, bool) or not isinstance(amount, (int, float, Decimal)):
        raise ValueError("Поле amount має бути числом")

    value = Decimal(str(amount))
    if not value.is_finite():
        raise ValueError("Поле amount має бути скінченним числом")
    if value < 0:
        raise ValueError("Поле amount не може бути від'ємним")
    return tx_date, tx_type, value


def monthly_balance(transactions, year, month):
    """Повертає баланс (доходи - витрати) за вказаний місяць."""
    if isinstance(month, bool) or not isinstance(month, int) or not 1 <= month <= 12:
        raise ValueError("Місяць має бути цілим числом від 1 до 12")
    if isinstance(year, bool) or not isinstance(year, int) or year < 1:
        raise ValueError("Рік має бути додатним цілим числом")

    parsed = [_parse(tx) for tx in transactions]  # перевіряємо всі записи

    balance = Decimal("0")
    for tx_date, tx_type, amount in parsed:
        if tx_date.year == year and tx_date.month == month:
            balance += amount if tx_type == INCOME else amount
    return float(round(balance, 2))
