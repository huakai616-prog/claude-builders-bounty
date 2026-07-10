#!/usr/bin/env python3
"""Claude Code PreToolUse hook for blocking destructive Bash commands."""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


LOG_PATH = Path.home() / ".claude" / "hooks" / "blocked.log"


class BlockedCommand:
    def __init__(self, rule: str, reason: str) -> None:
        self.rule = rule
        self.reason = reason


def _has_rm_rf(command: str) -> bool:
    """Detect common recursive+force rm variants, including sudo and long flags."""
    try:
        import shlex

        tokens = shlex.split(command, posix=True)
    except ValueError:
        tokens = command.split()

    for index, token in enumerate(tokens):
        if Path(token).name != "rm":
            continue

        option_tokens = tokens[index + 1 :]
        has_recursive = False
        has_force = False

        for option in option_tokens:
            if option == "--":
                continue
            if not option.startswith("-"):
                continue

            if option in {"--recursive", "-r", "-R"}:
                has_recursive = True
            if option == "--force" or option == "-f":
                has_force = True

            if option.startswith("-") and not option.startswith("--"):
                flags = option.lstrip("-")
                if "r" in flags or "R" in flags:
                    has_recursive = True
                if "f" in flags:
                    has_force = True

        if has_recursive and has_force:
            return True

    return False


def _delete_from_without_where(command: str) -> bool:
    lowered = command.lower()
    for match in re.finditer(r"\bdelete\s+from\b", lowered):
        remainder = lowered[match.end() :]
        statement = re.split(r";|\n|\r|&&|\|\|", remainder, maxsplit=1)[0]
        if not re.search(r"\bwhere\b", statement):
            return True
    return False


def evaluate_command(command: str) -> BlockedCommand | None:
    if _has_rm_rf(command):
        return BlockedCommand("rm -rf", "Recursive forced deletion is blocked.")

    if re.search(r"\bdrop\s+table\b", command, flags=re.IGNORECASE):
        return BlockedCommand("DROP TABLE", "Dropping database tables is blocked.")

    if re.search(
        r"\bgit\s+push\b(?=.*(?:--force(?:-with-lease)?|-f)\b)",
        command,
        flags=re.IGNORECASE,
    ):
        return BlockedCommand("git push --force", "Force-pushing git history is blocked.")

    if re.search(r"\btruncate\b", command, flags=re.IGNORECASE):
        return BlockedCommand("TRUNCATE", "Truncating data is blocked.")

    if _delete_from_without_where(command):
        return BlockedCommand(
            "DELETE FROM without WHERE",
            "DELETE FROM statements must include a WHERE clause.",
        )

    return None


def _extract_command(payload: dict[str, Any]) -> str:
    tool_input = payload.get("tool_input", {})
    if not isinstance(tool_input, dict):
        return ""
    command = tool_input.get("command", "")
    return command if isinstance(command, str) else ""


def _project_path(payload: dict[str, Any]) -> str:
    cwd = payload.get("cwd")
    if isinstance(cwd, str) and cwd:
        return cwd
    env_project = os.environ.get("CLAUDE_PROJECT_DIR")
    if env_project:
        return env_project
    return os.getcwd()


def log_blocked_attempt(
    *,
    command: str,
    project_path: str,
    rule: str,
    log_path: Path = LOG_PATH,
) -> None:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "attempted_command": command,
        "project_path": project_path,
        "rule": rule,
    }
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(entry, ensure_ascii=False) + "\n")


def deny(reason: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        print(f"Invalid hook input JSON: {exc}", file=sys.stderr)
        return 1

    if payload.get("tool_name") != "Bash":
        return 0

    command = _extract_command(payload)
    blocked = evaluate_command(command)
    if blocked is None:
        return 0

    project_path = _project_path(payload)
    try:
        log_blocked_attempt(
            command=command,
            project_path=project_path,
            rule=blocked.rule,
        )
    except OSError as exc:
        print(f"Could not write blocked command log: {exc}", file=sys.stderr)

    deny(f"{blocked.reason} Rule: {blocked.rule}. Project: {project_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
