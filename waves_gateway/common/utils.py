"""
Utilities
"""

from decimal import Decimal
from fractions import Fraction
from numbers import Number
from typing import Any, Optional, Iterable
from math import modf


def _parse_value(value: Any) -> Fraction:
    """
    Ensures that the given value has the type Fraction.
    """

    if isinstance(value, Decimal) or isinstance(value, float) or isinstance(value, int):
        return Fraction(value)  # type: ignore
    elif isinstance(value, Fraction):
        return value
    else:
        raise TypeError("The given value is neither a Decimal, float or Fraction")


def _assert_no_fractional(value: Any, msg="is not fractional"):
    if modf(value)[0] != 0.0:
        raise ArithmeticError(msg)


def convert_to_int(value: Any, factor: Any) -> int:
    """
    Converts the given value to an integer by first multiplying it with the given factor and then
    casting the result to an integer. Information may get lost if the factor is too low.
    """
    parsed_v = _parse_value(value)

    parsed_factor = _parse_value(factor)

    _assert_no_fractional(parsed_factor, "factor cannot be a fraction; the factor is " + str(parsed_factor))

    return round(parsed_v * parsed_factor)


def convert_to_decimal(amount: int, factor: Number, precision: Optional[int] = None) -> Decimal:
    """
    Converts the given value to a Decimal by first dividing it by the given factor and then
    casting the result to a Decimal.
    If a precision is provided, round will be called with the result and the given precision.

    """
    parsed_v = _parse_value(amount)
    parsed_factor = _parse_value(factor)

    _assert_no_fractional(parsed_factor, "factor cannot be a fraction; the factor is " + str(parsed_factor))

    res = parsed_v / parsed_factor

    if precision is not None:
        return round(Decimal(float(res)), precision)  # type: ignore
    else:
        return Decimal(float(res))


def map_array(func, arr: list) -> list:
    """
    Calls the given function on every element on the given array and returns the resulting elements.
    """
    res = list()

    for el in arr:
        res.append(func(el))

    return res


def filter_array(func, arr: Iterable) -> list:
    """
    Filters the arr using the given function. The function must return True or False whether
    the element should be part of the result or not.
    """
    res = list()

    for el in arr:
        if func(el):
            res.append(el)

    return res
