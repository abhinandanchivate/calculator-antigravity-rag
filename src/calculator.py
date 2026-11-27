"""Calculator library."""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Union

Number = Union[int, float, str, Decimal]

_QUANTIZE_EXP = Decimal("1e-10")


# Implements: DEC-002
class CalcError(Exception):
    """Unified calculator error with an UPPER_SNAKE_CASE code and message."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


# Implements: DEC-001, DEC-002
def _to_decimal(value: Number) -> Decimal:
    """Convert a numeric input to Decimal without exposing built-in errors."""
    if isinstance(value, bool):
        raise CalcError("INVALID_INPUT", f"Invalid operand: {value!r}")
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise CalcError("INVALID_INPUT", f"Invalid operand: {value!r}") from exc


# Implements: DEC-001
def _round(value: Decimal) -> Decimal:
    """Round a Decimal result to 10 decimal places using ROUND_HALF_UP."""
    return value.quantize(_QUANTIZE_EXP, rounding=ROUND_HALF_UP)


# Implements: REQ-001, DEC-001, DEC-002
def add(a: Number, b: Number) -> Decimal:
    """Return a + b using Decimal arithmetic."""
    return _round(_to_decimal(a) + _to_decimal(b))


# Implements: REQ-001, DEC-001, DEC-002
def subtract(a: Number, b: Number) -> Decimal:
    """Return a - b using Decimal arithmetic."""
    return _round(_to_decimal(a) - _to_decimal(b))


# Implements: REQ-002, DEC-001, DEC-002
def multiply(a: Number, b: Number) -> Decimal:
    """Return a * b using Decimal arithmetic."""
    return _round(_to_decimal(a) * _to_decimal(b))


# Implements: REQ-002, DEC-001, DEC-002
def divide(a: Number, b: Number) -> Decimal:
    """Return a / b using Decimal arithmetic."""
    numerator = _to_decimal(a)
    denominator = _to_decimal(b)
    if denominator == 0:
        raise CalcError("DIVISION_BY_ZERO", "Cannot divide by zero")
    return _round(numerator / denominator)
