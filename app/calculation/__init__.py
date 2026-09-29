"""Calculation classes and the ``CalculationFactory``.

A *calculation* pairs two operands with an operation. Concrete
calculations register themselves with the factory via a decorator, so
adding a new operation never requires editing the factory (open/closed
principle).
"""

from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Type

from app.operation import Number, Operation


class Calculation(ABC):
    """Abstract base class for every calculation."""

    symbol: str = "?"

    def __init__(self, a: Number, b: Number) -> None:
        self.a = a
        self.b = b

    @abstractmethod
    def execute(self) -> Number:
        """Perform the calculation and return the result."""
        pass  # pragma: no cover

    def __str__(self) -> str:
        """Human-readable form, e.g. ``'2 + 3 = 5'``."""
        return f"{self.a} {self.symbol} {self.b} = {self.execute()}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(a={self.a!r}, b={self.b!r})"


class CalculationFactory:
    """Creates calculation instances from an operation name."""

    _calculations: Dict[str, Type[Calculation]] = {}

    @classmethod
    def register(cls, name: str) -> Callable[[Type[Calculation]], Type[Calculation]]:
        """Class decorator that registers a calculation under ``name``."""

        def decorator(calc_cls: Type[Calculation]) -> Type[Calculation]:
            key = name.lower()
            if key in cls._calculations:
                raise ValueError(f"Calculation '{name}' is already registered.")
            cls._calculations[key] = calc_cls
            return calc_cls

        return decorator

    @classmethod
    def create(cls, name: str, a: Number, b: Number) -> Calculation:
        """Return a calculation instance for ``name``.

        Raises:
            ValueError: if ``name`` is not a registered operation.
        """
        calc_cls = cls._calculations.get(name.lower())
        if calc_cls is None:
            available = ", ".join(cls.available())
            raise ValueError(
                f"Unsupported operation: '{name}'. Available: {available}"
            )
        return calc_cls(a, b)

    @classmethod
    def available(cls) -> List[str]:
        """Return the sorted list of registered operation names."""
        return sorted(cls._calculations)


@CalculationFactory.register("add")
class AddCalculation(Calculation):
    """Addition: ``a + b``."""

    symbol = "+"

    def execute(self) -> Number:
        return Operation.addition(self.a, self.b)


@CalculationFactory.register("subtract")
class SubtractCalculation(Calculation):
    """Subtraction: ``a - b``."""

    symbol = "-"

    def execute(self) -> Number:
        return Operation.subtraction(self.a, self.b)


@CalculationFactory.register("multiply")
class MultiplyCalculation(Calculation):
    """Multiplication: ``a * b``."""

    symbol = "*"

    def execute(self) -> Number:
        return Operation.multiplication(self.a, self.b)


@CalculationFactory.register("divide")
class DivideCalculation(Calculation):
    """Division: ``a / b``."""

    symbol = "/"

    def execute(self) -> Number:
        return Operation.division(self.a, self.b)
