---
name: test-report
description: Report the result of the automatic post-change test run to the user. Invoke only when a Stop hook hands you test results ("A hook ran the tests for the code you just changed"). Report only; never fix, analyze or re-run.
---

# Test report

A Stop hook has already decided that code changed, picked only the tests of the
changed components, and run them. You received the result. Your job is to relay
it, nothing more.

## Do
- Start with one status line: `Tests: PASSED` or `Tests: FAILED`.
- Say which test files ran (that tells the user which components were checked).
- For a pass: add the count from the pytest summary (e.g. "6 passed").
- For a failure: list each failing test name and, for each, the one-line
  assertion or error message copied from the output.
- If the hook says no tests exist for a component, say so in one line.
- Stop after the report.

## Don't
- Don't run tests (pytest or anything else). The hook owns that.
- Don't fix code, edit files, or propose a patch.
- Don't analyze causes or speculate about why something failed.
- Don't read other files or run any other tool.
- Don't repeat the whole pytest output; summarize as above.

## Example

```
Tests: FAILED
Ran: tests/test_event_bus.py
- test_events_arrive_in_order: assert PartialText(text='b') == PartialText(text='a')
```
