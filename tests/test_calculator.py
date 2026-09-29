"""Unit tests for the Calculator REPL."""

import pytest

import main
from app.calculator import HELP_TEXT, Calculator


def make_calculator(inputs):
    """Build a Calculator fed by ``inputs`` that records its output."""
    feed = iter(inputs)
    output = []

    def fake_input(_prompt):
        try:
            return next(feed)
        except StopIteration:
            raise EOFError from None

    return Calculator(input_func=fake_input, output_func=output.append), output


# ---------------------------------------------------------------------- #
# parse_number (EAFP)
# ---------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "token, expected",
    [("5", 5), ("-3", -3), ("2.5", 2.5), ("4.0", 4), ("1e3", 1000), ("-0.25", -0.25)],
)
def test_parse_number_valid(token, expected):
    value = Calculator.parse_number(token)
    assert value == expected
    assert type(value) is type(expected)


@pytest.mark.parametrize("token", ["abc", "1,5", "", "two", "3..4"])
def test_parse_number_invalid(token):
    with pytest.raises(ValueError, match="Invalid number"):
        Calculator.parse_number(token)


@pytest.mark.parametrize("token", ["inf", "-inf", "nan"])
def test_parse_number_rejects_non_finite(token):
    with pytest.raises(ValueError, match="must be finite"):
        Calculator.parse_number(token)


# ---------------------------------------------------------------------- #
# parse_input (LBYL)
# ---------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "line, expected",
    [
        ("add 1 2", ("add", 1, 2)),
        ("ADD 1 2", ("add", 1, 2)),
        ("+ 1 2", ("add", 1, 2)),
        ("- 5 2", ("subtract", 5, 2)),
        ("* 3 4", ("multiply", 3, 4)),
        ("x 3 4", ("multiply", 3, 4)),
        ("/ 8 2", ("divide", 8, 2)),
        ("  divide   9   3  ", ("divide", 9, 3)),
    ],
)
def test_parse_input_valid(line, expected):
    assert Calculator.parse_input(line) == expected


@pytest.mark.parametrize("line", ["add", "add 1", "add 1 2 3", "1 2"])
def test_parse_input_wrong_token_count(line):
    with pytest.raises(ValueError, match="Expected format"):
        Calculator.parse_input(line)


# ---------------------------------------------------------------------- #
# handle / evaluate
# ---------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "line, expected",
    [
        ("add 2 3", "Result: 2 + 3 = 5"),
        ("subtract 2 3", "Result: 2 - 3 = -1"),
        ("multiply 2.5 4", "Result: 2.5 * 4 = 10.0"),
        ("divide 7 2", "Result: 7 / 2 = 3.5"),
    ],
)
def test_handle_calculation(line, expected):
    calc, output = make_calculator([])
    assert calc.handle(line) is True
    assert output == [expected]
    assert len(calc.history) == 1


@pytest.mark.parametrize(
    "line, message",
    [
        ("divide 1 0", "Error: Division by zero is not allowed."),
        ("add one 2", "Error: Invalid number: 'one'"),
        ("add 1", "Error: Expected format"),
        ("power 2 3", "Error: Unsupported operation: 'power'"),
    ],
)
def test_handle_errors_do_not_crash_or_record(line, message):
    calc, output = make_calculator([])
    assert calc.handle(line) is True
    assert output[0].startswith(message)
    assert calc.history == []


def test_handle_blank_line():
    calc, output = make_calculator([])
    assert calc.handle("   ") is True
    assert output == []


@pytest.mark.parametrize("command", ["exit", "EXIT", "quit", " exit "])
def test_handle_exit(command):
    calc, output = make_calculator([])
    assert calc.handle(command) is False
    assert output == ["Goodbye!"]


def test_help_command():
    calc, output = make_calculator([])
    assert calc.handle("help") is True
    assert output == [HELP_TEXT]


def test_history_empty():
    calc, output = make_calculator([])
    calc.handle("history")
    assert output == ["No calculations yet."]


def test_history_lists_calculations():
    calc, output = make_calculator([])
    calc.handle("add 1 2")
    calc.handle("multiply 3 4")
    output.clear()
    calc.handle("history")
    assert output == ["1. 1 + 2 = 3", "2. 3 * 4 = 12"]


def test_clear_history():
    calc, output = make_calculator([])
    calc.handle("add 1 2")
    calc.handle("clear")
    assert calc.history == []
    assert output[-1] == "History cleared."


# ---------------------------------------------------------------------- #
# run (the REPL loop)
# ---------------------------------------------------------------------- #
def test_run_full_session():
    calc, output = make_calculator(["add 2 3", "divide 1 0", "history", "exit", "add 9 9"])
    calc.run()
    assert output[0].startswith("Welcome")
    assert "Result: 2 + 3 = 5" in output
    assert "Error: Division by zero is not allowed." in output
    assert "1. 2 + 3 = 5" in output
    assert output[-1] == "Goodbye!"
    assert len(calc.history) == 1  # "add 9 9" after exit is never read


def test_run_handles_eof():
    calc, output = make_calculator([])
    calc.run()
    assert output[-1] == "\nGoodbye!"


def test_run_handles_keyboard_interrupt():
    def interrupt(_prompt):
        raise KeyboardInterrupt

    output = []
    Calculator(input_func=interrupt, output_func=output.append).run()
    assert output[-1] == "\nGoodbye!"


def test_main_entry_point(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _prompt: "exit")
    main.main()
    assert "Goodbye!" in capsys.readouterr().out
