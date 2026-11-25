from datetime import date

import pytest

from balance import monthly_balance


def tx(day, kind, amount, month=11, year=2026):
    return {"date": date(year, month, day), "type": kind, "amount": amount}


# --- критерій 1: баланс = доходи - витрати ---

def test_income_minus_expenses():
    data = [tx(1, "income", 1000), tx(5, "expense", 400), tx(10, "expense", 100.50)]
    assert monthly_balance(data, 2026, 11) == 499.5


def test_only_expenses_give_negative_balance():
    data = [tx(3, "expense", 250), tx(4, "expense", 50)]
    assert monthly_balance(data, 2026, 11) == -300


def test_kopecks_without_float_errors():
    data = [tx(1, "income", 0.1), tx(2, "income", 0.2)]
    assert monthly_balance(data, 2026, 11) == 0.3


def test_zero_amount_does_not_change_balance():
    data = [tx(1, "income", 0), tx(2, "expense", 0)]
    assert monthly_balance(data, 2026, 11) == 0


# --- критерій 2: враховується лише обраний місяць ---

def test_other_months_and_years_are_ignored():
    data = [
        tx(15, "income", 500),
        tx(15, "income", 999, month=10),
        tx(15, "income", 777, year=2025),
    ]
    assert monthly_balance(data, 2026, 11) == 500


def test_month_boundaries():
    data = [
        tx(1, "income", 100),               # перший день місяця
        tx(30, "income", 200),              # останній день місяця
        tx(31, "income", 999, month=10),    # день до початку
        tx(1, "income", 999, month=12),     # день після кінця
    ]
    assert monthly_balance(data, 2026, 11) == 300


def test_leap_day_counts_in_february():
    data = [{"date": date(2024, 2, 29), "type": "income", "amount": 80}]
    assert monthly_balance(data, 2024, 2) == 80


# --- критерій 3: немає транзакцій -> 0 ---

def test_empty_list_gives_zero():
    assert monthly_balance([], 2026, 11) == 0


# --- критерій 4: некоректні дані -> ValueError ---

def test_negative_amount_raises():
    with pytest.raises(ValueError):
        monthly_balance([tx(1, "income", -5)], 2026, 11)


@pytest.mark.parametrize("bad_amount", ["100", None, True, float("nan")])
def test_non_numeric_amount_raises(bad_amount):
    with pytest.raises(ValueError):
        monthly_balance([tx(1, "income", bad_amount)], 2026, 11)


def test_unknown_type_raises():
    with pytest.raises(ValueError):
        monthly_balance([tx(1, "refund", 10)], 2026, 11)


@pytest.mark.parametrize("bad_month", [0, 13, -1, "11", None])
def test_invalid_month_raises(bad_month):
    with pytest.raises(ValueError):
        monthly_balance([], 2026, bad_month)


def test_invalid_date_type_raises():
    data = [{"date": "2026-11-05", "type": "income", "amount": 10}]
    with pytest.raises(ValueError):
        monthly_balance(data, 2026, 11)


def test_missing_field_raises():
    with pytest.raises(ValueError):
        monthly_balance([{"type": "income", "amount": 10}], 2026, 11)


def test_invalid_transaction_in_other_month_still_raises():
    with pytest.raises(ValueError):
        monthly_balance([tx(1, "income", -5, month=10)], 2026, 11)
