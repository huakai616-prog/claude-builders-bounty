#!/usr/bin/env python3
"""Validate the Next.js SQLite SaaS CLAUDE.md template."""

from __future__ import annotations

from pathlib import Path


TEMPLATE_PATH = Path(__file__).with_name("CLAUDE.md")


def require(text: str, label: str, needle: str) -> None:
    if needle not in text:
        raise SystemExit(f"Missing {label}: {needle}")


def main() -> int:
    text = TEMPLATE_PATH.read_text(encoding="utf-8")

    for section in [
        "## Stack & Versions",
        "## Dev Commands",
        "## Folder Structure",
        "## Naming Conventions",
        "## SQL / Migration Conventions",
        "## Component Patterns",
        "## Patterns To Follow",
        "## What We Don't Do (And Why)",
    ]:
        require(text, "section", section)

    for marker in [
        "Next.js 15 App Router",
        "SQLite",
        "better-sqlite3",
        "Turso",
        "Drizzle",
        "pnpm",
        "Server Components",
        "migrations are append-only",
        "Every table has `id`, `created_at`, and `updated_at`",
        "Every rule has a reason",
    ]:
        require(text, "acceptance marker", marker)

    if text.count("Reason:") < 35:
        raise SystemExit("Expected at least 35 opinionated rules with reasons")

    print("template-ok")
    print(f"reasoned_rules={text.count('Reason:')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
