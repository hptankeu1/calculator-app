"""Parameterized unit tests for app.calculation."""

import pytest

from app.calculation import (
    AddCalculation,
    Calculation,
    CalculationFactory,
    DivideCalculation,
    MultiplyCalculation,
    SubtractCalculation,
)


@pytest.mark.parametrize(
    "name, a, b, expected_cls, expected_result",
    [
        ("add", 2, 3, AddCalculation, 5),
        ("subtract", 10, 4, SubtractCalculation, 6),
        ("multiply", 3, 4, MultiplyCalculation, 12),
        ("divide", 9, 2, DivideCalculation, 4.5),
        ("ADD", 1, 1, AddCalculation, 2),  # names are case-insensitive
        ("Divide", -8, 4, DivideCalculation, -2),
    ],
)
def test_factory_creates_correct_calculation(name, a, b, expected_cls, expected_result):
    calc = CalculationFactory.create(name, a, b)
    assert isinstance(calc, expected_cls)
    assert calc.execute() == expected_result


@pytest.mark.parametrize("name", ["power", "mod", "", "addition"])
def test_factory_rejects_unknown_operation(name):
    with pytest.raises(ValueError, match="Unsupported operation"):
        CalculationFactory.create(name, 1, 2)


def test_factory_available_lists_operations():
    assert CalculationFactory.available() == ["add", "divide", "multiply", "subtract"]


def test_factory_rejects_duplicate_registration():
    with pytest.raises(ValueError, match="already registered"):

        @CalculationFactory.register("add")
        class Duplicate(Calculation):  # pylint: disable=unused-variable
            def execute(self):
                return 0


def test_factory_register_new_operation():
    @CalculationFactory.register("power")
    class PowerCalculation(Calculation):
        symbol = "^"

        def execute(self):
            return self.a ** self.b

    try:
        calc = CalculationFactory.create("power", 2, 3)
        assert isinstance(calc, PowerCalculation)
        assert str(calc) == "2 ^ 3 = 8"
    finally:
        # Keep the registry clean for other tests.
        del CalculationFactory._calculations["power"]


@pytest.mark.parametrize(
    "calc, expected",
    [
        (AddCalculation(2, 3), "2 + 3 = 5"),
        (SubtractCalculation(5, 7), "5 - 7 = -2"),
        (MultiplyCalculation(2.5, 2), "2.5 * 2 = 5.0"),
        (DivideCalculation(1, 4), "1 / 4 = 0.25"),
    ],
)
def test_calculation_str(calc, expected):
    assert str(calc) == expected


def test_calculation_repr():
    assert repr(AddCalculation(1, 2)) == "AddCalculation(a=1, b=2)"


def test_divide_calculation_by_zero_raises():
    with pytest.raises(ValueError, match="Division by zero"):
        DivideCalculation(1, 0).execute()


def test_calculation_is_abstract():
    with pytest.raises(TypeError):
        Calculation(1, 2)  # pylint: disable=abstract-class-instantiated
