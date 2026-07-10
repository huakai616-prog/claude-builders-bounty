# Next.js 15 + SQLite SaaS CLAUDE.md Template

This template is an opinionated `CLAUDE.md` for a greenfield SaaS project using Next.js 15 App Router and SQLite through `better-sqlite3` or Turso/libSQL.

## Use

1. Copy `CLAUDE.md` into the root of a new Next.js 15 project.
2. Keep the defaults unless the project owner explicitly changes the stack.
3. Ask Claude Code to implement a vertical slice, such as "create projects with owner-only editing".

## What It Covers

- Stack and version defaults.
- Folder structure for App Router, database code, services, and features.
- Naming conventions for routes, components, actions, services, tables, and columns.
- SQL and migration rules for Drizzle, SQLite, transactions, indexes, and timestamps.
- Component patterns for Server Components, Client Components, server actions, and SaaS dashboard states.
- What we don't do and why, so Claude Code has decision pressure instead of generic advice.

## Validation

```bash
python3 templates/nextjs-sqlite-saas/validate_template.py
```

The validation script checks the expected sections and key acceptance criteria from issue #2.
