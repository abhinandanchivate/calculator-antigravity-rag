"""Tests for calculator library."""

from decimal import Decimal

from src.calculator import add, divide, multiply, subtract


# Tests: REQ-001
def test_add_integers() -> None:
    assert add(2, 3) == Decimal("5")


# Tests: REQ-001
def test_subtract_negative_result() -> None:
    assert subtract(2, 5) == Decimal("-3")


# Tests: REQ-001
def test_add_decimal_precision() -> None:
    assert add(0.1, 0.2) == Decimal("0.3")


# Tests: REQ-002
def test_multiply() -> None:
    assert multiply(4, 2.5) == Decimal("10")


# Tests: REQ-002
def test_divide() -> None:
    assert divide(10, 4) == Decimal("2.5")
