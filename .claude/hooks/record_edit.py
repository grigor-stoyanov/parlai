"""PostToolUse hook: remember which project files were edited this turn.

Claude Code sends JSON on stdin describing the tool call. We append the edited
file's path (relative to the project) to .claude/.edited-files. The Stop hook
(run_tests.py) reads that list at the end of the turn.
"""

import json
import os
import sys
from pathlib import Path

project = Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()
edited_list = project / ".claude" / ".edited-files"

payload = json.load(sys.stdin)
file_path = payload.get("tool_input", {}).get("file_path")
if not file_path:
    sys.exit(0)

try:
    relative = Path(file_path).resolve().relative_to(project)
except ValueError:
    sys.exit(0)  # file is outside the project, not our business

with edited_list.open("a") as f:
    f.write(f"{relative}\n")
