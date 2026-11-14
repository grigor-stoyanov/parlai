"""Main loop: wires the packages in src/ together.

Run with `uv run python main.py` (or the project's .venv interpreter in PyCharm).
"""

import argparse


def main(argv: list[str] | None = None) -> None:
    # argv is injectable so tests don't parse pytest's own command-line flags.
    parser = argparse.ArgumentParser(prog="parlai", description="Talk to AI with your voice.")
    parser.parse_args(argv)
    print("parlai: nothing to run yet (scaffold only).")


if __name__ == "__main__":
    main()
