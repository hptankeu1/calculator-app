# Command-Line Calculator

![CI](https://github.com/hptankeu1/calculator-app/actions/workflows/python-app.yml/badge.svg)

A modular, professional-grade command-line calculator written in Python. It runs as an interactive REPL, keeps a history of the session's calculations, handles bad input gracefully, and is covered by a pytest suite at **100% line and branch coverage**, enforced by GitHub Actions on every push.

## Features

- **REPL interface** – read, evaluate, print, loop until you type `exit`
- **Four operations** – add, subtract, multiply, divide (with symbol shortcuts `+ - * x /`)
- **Session history** – `history` lists every successful calculation; `clear` empties it
- **Input validation** – wrong argument count, non-numeric values, `inf`/`nan`, unknown operations and division by zero all produce a clear error message instead of a crash
- **Factory pattern** – `CalculationFactory` builds calculation objects from the operation name; new operations register themselves with a decorator

## Project structure

```
calculator-app/
├── app/
│   ├── __init__.py
│   ├── calculator/__init__.py    # Calculator class: REPL, commands, history
│   ├── calculation/__init__.py   # Calculation ABC, concrete classes, CalculationFactory
│   └── operation/__init__.py     # Operation: pure arithmetic functions
├── tests/
│   ├── test_operations.py        # parameterized tests for Operation
│   ├── test_calculations.py      # parameterized tests for calculations + factory
│   └── test_calculator.py        # REPL, parsing, commands, error handling
├── .github/workflows/python-app.yml
├── .coveragerc
├── pytest.ini
├── requirements.txt
└── main.py                       # entry point
```

## Setup

Requires Python 3.8+.

```bash
git clone https://github.com/hptankeu1/calculator-app.git
cd calculator-app

python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

Enter an operation followed by two numbers:

```
Welcome to the calculator! Type 'help' for instructions.
calc> add 2 3
Result: 2 + 3 = 5
calc> / 10 4
Result: 10 / 4 = 2.5
calc> divide 5 0
Error: Division by zero is not allowed.
calc> add x 2
Error: Invalid number: 'x'
calc> history
1. 2 + 3 = 5
2. 10 / 4 = 2.5
calc> exit
Goodbye!
```

| Command   | Description                          |
|-----------|--------------------------------------|
| `help`    | Show usage instructions              |
| `history` | List calculations from this session  |
| `clear`   | Clear the history                    |
| `exit`    | Quit (also `quit`, Ctrl+D, Ctrl+C)   |

## Design notes

**Layers.** `Operation` holds the raw arithmetic. Each `Calculation` subclass pairs two operands with one operation. `Calculator` handles user interaction only. Each layer can be tested on its own.

**DRY.** Operations are written once and reused by the calculations. `__str__` lives in the base class and uses each subclass's `symbol`. Special commands go through a dispatch dictionary rather than an `if/elif` chain.

**Error handling – LBYL and EAFP.**

- *LBYL (Look Before You Leap)*: `Operation.division` checks `b == 0` before dividing, and `Calculator.parse_input` checks the token count before unpacking.
- *EAFP (Easier to Ask Forgiveness than Permission)*: `Calculator.parse_number` just tries `float(token)` and converts the `ValueError` into a friendly message. The REPL's `handle` method wraps evaluation in `try/except ValueError`, and `run` catches `EOFError`/`KeyboardInterrupt` to exit cleanly.

**Testability.** `Calculator` accepts injectable `input_func` and `output_func`, so tests drive full REPL sessions without a terminal.

## Testing

```bash
pytest --cov=app tests/
coverage report --fail-under=100
```

Coverage is configured in `.coveragerc` with branch coverage on. The only exclusions are marked `# pragma: no cover`: the `pass` body of the abstract `Calculation.execute` method and the `if __name__ == "__main__":` guard in `main.py`.

## Continuous integration

`.github/workflows/python-app.yml` runs on every push and pull request to `main`. It installs dependencies, runs the test suite with coverage, and fails the build if coverage drops below 100%.
