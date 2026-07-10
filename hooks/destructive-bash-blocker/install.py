#!/usr/bin/env python3
"""Install the destructive Bash command blocker into ~/.claude/hooks."""

from __future__ import annotations

import json
import os
import shutil
import stat
from pathlib import Path
from typing import Any


HOOK_NAME = "block_destructive_bash.py"
HOOK_SOURCE = Path(__file__).with_name(HOOK_NAME)
CLAUDE_DIR = Path.home() / ".claude"
HOOKS_DIR = CLAUDE_DIR / "hooks"
SETTINGS_PATH = CLAUDE_DIR / "settings.json"


def _load_settings(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as settings_file:
        data = json.load(settings_file)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def _hook_entry(installed_hook: Path) -> dict[str, Any]:
    return {
        "type": "command",
        "command": str(installed_hook),
        "args": [],
    }


def _ensure_hook_config(settings: dict[str, Any], installed_hook: Path) -> bool:
    hooks = settings.setdefault("hooks", {})
    pre_tool_use = hooks.setdefault("PreToolUse", [])
    entry = _hook_entry(installed_hook)

    for group in pre_tool_use:
        if group.get("matcher") != "Bash":
            continue
        group_hooks = group.setdefault("hooks", [])
        if any(hook.get("command") == str(installed_hook) for hook in group_hooks):
            return False
        group_hooks.append(entry)
        return True

    pre_tool_use.append({"matcher": "Bash", "hooks": [entry]})
    return True


def install() -> None:
    HOOKS_DIR.mkdir(parents=True, exist_ok=True)
    installed_hook = HOOKS_DIR / HOOK_NAME
    shutil.copy2(HOOK_SOURCE, installed_hook)
    installed_hook.chmod(installed_hook.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    settings = _load_settings(SETTINGS_PATH)
    _ensure_hook_config(settings, installed_hook)

    tmp_path = SETTINGS_PATH.with_suffix(".json.tmp")
    with tmp_path.open("w", encoding="utf-8") as settings_file:
        json.dump(settings, settings_file, indent=2)
        settings_file.write("\n")
    os.replace(tmp_path, SETTINGS_PATH)

    print(f"Installed {installed_hook}")
    print(f"Updated {SETTINGS_PATH}")


if __name__ == "__main__":
    install()
