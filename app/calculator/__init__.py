"""Calculator REPL (Read-Eval-Print Loop).

The ``Calculator`` class reads a line from the user, evaluates it as a
command or a calculation, prints the result, and loops until the user
exits. Input and output functions are injectable so the REPL can be
tested without a real terminal.
"""

import math
from typing import Callable, List, Optional, Tuple

from app.calculation import Calculation, CalculationFactory
from app.operation import Number

# Symbol shortcuts, so "+ 2 3" works the same as "add 2 3".
ALIASES = {"+": "add", "-": "subtract", "*": "multiply", "x": "multiply", "/": "divide"}

HELP_TEXT = """\
Usage:  <operation> <number1> <number2>
  Operations: add (+), subtract (-), multiply (* or x), divide (/)
  Example:    add 2 3      ->  2 + 3 = 5
              / 10 4       ->  10 / 4 = 2.5

Commands:
  help      Show this message
  history   Show calculations from this session
  clear     Clear the history
  exit      Quit the calculator"""


class Calculator:
    """Interactive command-line calculator with session history."""

    PROMPT = "calc> "

    def __init__(
        self,
        input_func: Optional[Callable[[str], str]] = None,
        output_func: Optional[Callable[[str], None]] = None,
    ) -> None:
        # Resolved at call time so tests can monkeypatch builtins.
        self._input = input_func or input
        self._output = output_func or print
        self.history: List[Calculation] = []
        # Dispatch table for special commands (avoids an if/elif chain).
        self._commands = {
            "help": self.show_help,
            "history": self.show_history,
            "clear": self.clear_history,
        }

    # ------------------------------------------------------------------ #
    # Commands
    # ------------------------------------------------------------------ #
    def show_help(self) -> None:
        """Print usage instructions."""
        self._output(HELP_TEXT)

    def show_history(self) -> None:
        """Print every calculation performed this session."""
        if not self.history:
            self._output("No calculations yet.")
            return
        for index, calc in enumerate(self.history, start=1):
            self._output(f"{index}. {calc}")

    def clear_history(self) -> None:
        """Empty the session history."""
        self.history.clear()
        self._output("History cleared.")

    # ------------------------------------------------------------------ #
    # Parsing and evaluation
    # ------------------------------------------------------------------ #
    @staticmethod
    def parse_number(token: str) -> Number:
        """Convert ``token`` to a number.

        EAFP (Easier to Ask Forgiveness than Permission): we simply try
        the conversion and translate the failure into a friendly error,
        instead of pre-checking the string with regexes.
        Whole numbers come back as ``int`` so results read naturally.
        """
        try:
            value = float(token)
        except ValueError:
            raise ValueError(f"Invalid number: '{token}'") from None
        if not math.isfinite(value):
            raise ValueError(f"Invalid number: '{token}' (must be finite)")
        return int(value) if value.is_integer() else value

    @classmethod
    def parse_input(cls, line: str) -> Tuple[str, Number, Number]:
        """Split a line into ``(operation, a, b)``.

        LBYL: the token count is checked *before* unpacking, so the user
        gets a clear message rather than an unpacking error.
        """
        tokens = line.split()
        if len(tokens) != 3:
            raise ValueError(
                "Expected format: <operation> <number1> <number2> "
                "(type 'help' for examples)"
            )
        op, raw_a, raw_b = tokens
        op = ALIASES.get(op, op.lower())
        return op, cls.parse_number(raw_a), cls.parse_number(raw_b)

    def evaluate(self, line: str) -> Calculation:
        """Create and run a calculation, store it in history, and return it."""
        op, a, b = self.parse_input(line)
        calculation = CalculationFactory.create(op, a, b)
        calculation.execute()  # raises ValueError on e.g. division by zero
        self.history.append(calculation)
        return calculation

    def handle(self, line: str) -> bool:
        """Process one line of input. Return ``False`` when the user exits."""
        line = line.strip()
        if not line:
            return True
        command = line.lower()
        if command in ("exit", "quit"):
            self._output("Goodbye!")
            return False
        if command in self._commands:
            self._commands[command]()
            return True
        try:
            self._output(f"Result: {self.evaluate(line)}")
        except ValueError as error:
            self._output(f"Error: {error}")
        return True

    # ------------------------------------------------------------------ #
    # REPL
    # ------------------------------------------------------------------ #
    def run(self) -> None:
        """Start the Read-Eval-Print Loop."""
        self._output("Welcome to the calculator! Type 'help' for instructions.")
        while True:
            try:
                line = self._input(self.PROMPT)
            except (EOFError, KeyboardInterrupt):
                self._output("\nGoodbye!")
                break
            if not self.handle(line):
                break
