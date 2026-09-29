"""Parameterized unit tests for app.operation."""

import pytest

from app.operation import Operation


@pytest.mark.parametrize(
    "a, b, expected",
    [(2, 3, 5), (-1, 1, 0), (0, 0, 0), (2.5, 0.5, 3.0), (-4, -6, -10)],
)
def test_addition(a, b, expected):
    assert Operation.addition(a, b) == expected


@pytest.mark.parametrize(
    "a, b, expected",
    [(5, 3, 2), (3, 5, -2), (0, 0, 0), (2.5, 0.5, 2.0), (-4, -6, 2)],
)
def test_subtraction(a, b, expected):
    assert Operation.subtraction(a, b) == expected


@pytest.mark.parametrize(
    "a, b, expected",
    [(2, 3, 6), (-2, 3, -6), (0, 99, 0), (2.5, 2, 5.0), (-4, -6, 24)],
)
def test_multiplication(a, b, expected):
    assert Operation.multiplication(a, b) == expected


@pytest.mark.parametrize(
    "a, b, expected",
    [(6, 3, 2), (7, 2, 3.5), (-9, 3, -3), (0, 5, 0), (1, 4, 0.25)],
)
def test_division(a, b, expected):
    assert Operation.division(a, b) == pytest.approx(expected)


@pytest.mark.parametrize("a", [1, 0, -5, 2.5])
def test_division_by_zero_raises(a):
    with pytest.raises(ValueError, match="Division by zero"):
        Operation.division(a, 0)
