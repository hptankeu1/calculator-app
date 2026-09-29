"""Entry point: ``python main.py`` starts the calculator REPL."""

from app.calculator import Calculator


def main() -> None:
    """Run the interactive calculator."""
    Calculator().run()


if __name__ == "__main__":
    main()  # pragma: no cover
