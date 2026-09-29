"""Low-level arithmetic operations.

Each operation is a pure static method so it can be reused by any
calculation class without instantiating anything (DRY).
"""

from typing import Union

Number = Union[int, float]


class Operation:
    """Namespace for the four basic arithmetic operations."""

    @staticmethod
    def addition(a: Number, b: Number) -> Number:
        """Return the sum of ``a`` and ``b``."""
        return a + b

    @staticmethod
    def subtraction(a: Number, b: Number) -> Number:
        """Return ``a`` minus ``b``."""
        return a - b

    @staticmethod
    def multiplication(a: Number, b: Number) -> Number:
        """Return the product of ``a`` and ``b``."""
        return a * b

    @staticmethod
    def division(a: Number, b: Number) -> float:
        """Return ``a`` divided by ``b``.

        LBYL (Look Before You Leap): the divisor is checked *before*
        dividing, so a clear ``ValueError`` is raised instead of Python's
        generic ``ZeroDivisionError``.
        """
        if b == 0:
            raise ValueError("Division by zero is not allowed.")
        return a / b
