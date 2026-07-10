# Destructive Bash Blocker

Claude Code `PreToolUse` hook for blocking high-risk Bash commands before they run.

## Install

```bash
cd hooks/destructive-bash-blocker
python3 install.py
```

The installer copies `block_destructive_bash.py` into `~/.claude/hooks/`, marks it executable, and registers it in `~/.claude/settings.json` for the `Bash` tool.

## What It Blocks

- `rm -rf` and common flag variants such as `rm -fr`, `rm -r -f`, and `rm --recursive --force`
- `DROP TABLE`
- `git push --force`, `git push --force-with-lease`, and `git push -f`
- `TRUNCATE`
- `DELETE FROM` statements without a `WHERE` clause

Normal Bash commands exit silently with no decision, so Claude Code continues through its normal permission flow.

## Logging

Every blocked attempt is appended to:

```text
~/.claude/hooks/blocked.log
```

Each line is JSON with `timestamp`, `attempted_command`, `project_path`, and the matched `rule`.

## Manual Configuration

If you prefer not to run the installer, place `block_destructive_bash.py` in `~/.claude/hooks/`, make it executable, and add this to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "/Users/you/.claude/hooks/block_destructive_bash.py",
            "args": []
          }
        ]
      }
    ]
  }
}
```

## Test

```bash
python3 -m unittest discover -s hooks/destructive-bash-blocker/tests
```
