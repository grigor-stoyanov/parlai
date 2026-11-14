"""Stop hook: run only the tests that belong to the code changed this turn.

Flow:
1. Read the list of edited files that record_edit.py collected.
2. Map each edited file to the test files of its component (see find_tests).
3. If there is nothing to test, exit silently: Claude just stops as normal.
4. Otherwise run pytest on those test files only, then "block" the stop with the
   result as the reason. That sends the result back to Claude, which reports it
   to the user through the test-report skill. It does not fix anything.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

project = Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()
edited_list = project / ".claude" / ".edited-files"
MAX_OUTPUT_LINES = 40


def find_tests(path: Path) -> tuple[list[Path], str | None]:
    """Return (test files to run, component name with no tests or None)."""
    parts = path.parts
    if path.suffix != ".py":
        return [], None  # docs, config, etc. are not code under test
    if parts[0] == "tests":
        return ([path] if (project / path).exists() else []), None
    if path.name == "main.py" and len(parts) == 1:
        component = "main"
        pattern = "test_main*.py"
    elif parts[0] == "src" and len(parts) > 1:
        component = parts[1]
        pattern = f"test_{component}*.py"
    else:
        return [], None
    found = sorted((project / "tests").glob(pattern))
    if found:
        return [f.relative_to(project) for f in found], None
    return [], component


def main() -> None:
    payload = json.load(sys.stdin)
    if payload.get("stop_hook_active"):
        return  # we already blocked once this turn; never loop

    if not edited_list.exists():
        return
    edited = [Path(line) for line in edited_list.read_text().splitlines() if line]
    edited_list.unlink()  # clear first so we only ever report a change once

    test_files: list[Path] = []
    untested: list[str] = []
    for path in dict.fromkeys(edited):  # de-duplicate, keep order
        tests, missing = find_tests(path)
        test_files += [t for t in tests if t not in test_files]
        if missing and missing not in untested:
            untested.append(missing)

    if not test_files and not untested:
        return

    lines = []
    if test_files:
        names = " ".join(str(t) for t in test_files)
        result = subprocess.run(
            ["uv", "run", "pytest", "-q", "--no-header", *map(str, test_files)],
            cwd=project,
            capture_output=True,
            text=True,
            timeout=150,
        )
        status = "PASSED" if result.returncode == 0 else f"FAILED (exit code {result.returncode})"
        output = (result.stdout + result.stderr).strip().splitlines()
        lines.append(f"Ran: pytest {names}")
        lines.append(f"Result: {status}")
        lines.append("Output (last lines):")
        lines += output[-MAX_OUTPUT_LINES:]
    if untested:
        lines.append(f"No tests exist yet for: {', '.join(untested)}")

    reason = (
        "A hook ran the tests for the code you just changed. Results:\n\n"
        + "\n".join(lines)
        + "\n\nInvoke the test-report skill and follow it: report this to the user, "
        "do not fix, analyze or re-run anything."
    )
    print(json.dumps({"decision": "block", "reason": reason}))


main()
