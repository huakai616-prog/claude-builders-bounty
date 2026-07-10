# CLAUDE.md

This file is the operating guide for Claude Code in a greenfield SaaS built with Next.js 15 App Router and SQLite. Follow it before asking clarifying questions. If the task is compatible with these defaults, proceed with these decisions. Every rule has a reason so Claude Code can act without drifting into generic advice.

## Stack & Versions

- Runtime: Node.js 22 LTS, TypeScript strict mode, pnpm.
  Reason: one package manager and one modern runtime keep generated commands and lockfiles predictable.
- Framework: Next.js 15 App Router, React 19, Server Components by default.
  Reason: server-first data loading keeps SQLite access off the client and reduces hydration work.
- Styling: Tailwind CSS plus small local components in `src/components`.
  Reason: SaaS screens need consistent spacing and fast iteration without a heavy component framework.
- Database: SQLite locally through `better-sqlite3`; Turso/libSQL is allowed only when deployment needs hosted SQLite.
  Reason: local SQLite is simple and deterministic; Turso preserves the SQLite model in production.
- ORM/query layer: Drizzle ORM with explicit schema files.
  Reason: SQL stays visible while TypeScript checks table and column names.
- Validation: Zod at every server action, route handler, webhook, and form boundary.
  Reason: database constraints are not a substitute for typed user input checks.
- Auth: HttpOnly session cookies stored in SQLite; never localStorage tokens.
  Reason: cookies reduce XSS token exposure and work naturally with Server Components.
- Tests: Vitest for pure logic, Playwright for critical SaaS flows.
  Reason: most business rules are unit-testable, but signup, login, billing gates, and CRUD need browser coverage.

## Dev Commands

Use these command names unless `package.json` already defines stricter equivalents.

```bash
pnpm install
pnpm dev
pnpm lint
pnpm typecheck
pnpm test
pnpm test:e2e
pnpm db:generate
pnpm db:migrate
pnpm db:studio
pnpm build
```

If a command is missing, add it before using it. Do not switch to npm, yarn, Prisma, MongoDB, or a hosted Postgres service unless the user explicitly changes the stack.

## Folder Structure

Use this structure for new files:

```text
src/
  app/
    (marketing)/
    (auth)/
    app/
      layout.tsx
      page.tsx
    api/
  components/
    ui/
    forms/
    layout/
  db/
    schema/
    migrations/
    client.ts
    queries/
  features/
    accounts/
    billing/
    projects/
    users/
  lib/
    auth/
    env.ts
    errors.ts
    result.ts
  server/
    actions/
    services/
  tests/
```

Rules:

- Put route segments under `src/app`, not feature folders.
  Reason: App Router routing should stay visible from the filesystem.
- Put business logic in `src/server/services` or `src/features/*`, not in page components.
  Reason: services can be tested without rendering React.
- Put database reads and writes in `src/db/queries`.
  Reason: central query ownership makes transactions and indexes easier to audit.
- Put shared UI primitives in `src/components/ui`; put domain UI under `src/features/<domain>/components`.
  Reason: primitives stay generic while feature components can use domain language.
- Keep `src/lib/env.ts` as the only place that reads `process.env`.
  Reason: runtime configuration becomes typed, validated, and easy to mock.

## Naming Conventions

- Files and folders: kebab-case, except React components use PascalCase filenames only when the file exports exactly one component.
  Reason: route and utility paths remain URL-friendly; component files stay recognizable.
- React components: PascalCase nouns, such as `ProjectCard` and `InviteUserForm`.
  Reason: components should name the UI object they render.
- Server actions: verb-object names ending in `Action`, such as `createProjectAction`.
  Reason: action imports should make mutation intent obvious.
- Services: verb-object functions without framework terms, such as `createProject`.
  Reason: services should not care whether they are called by actions, jobs, or tests.
- Database tables: plural snake_case, such as `users`, `projects`, `project_members`.
  Reason: SQLite and SQL tools read snake_case naturally.
- Columns: snake_case in SQL, camelCase in TypeScript objects.
  Reason: SQL remains idiomatic while app code remains idiomatic.
- Booleans: prefix with `is_`, `has_`, or `can_` in SQL, and `is`, `has`, or `can` in TypeScript.
  Reason: boolean meaning should be clear at the callsite.

## SQL / Migration Conventions

- Schema lives in `src/db/schema/*.ts`; generated migration files live in `src/db/migrations`.
  Reason: schema is reviewed by humans; migrations are the historical record.
- Migrations are append-only after they are merged; migrations are append-only in every shared environment.
  Reason: editing old migrations breaks deployed databases and teammate environments.
- Every table has `id`, `created_at`, and `updated_at`.
  Reason: SaaS support and auditing need stable identifiers and timestamps.
- Use text UUID/ULID primary keys unless a table is purely internal and high-write.
  Reason: public IDs should not expose row counts.
- Add indexes for every foreign key and frequent lookup column.
  Reason: SQLite will not rescue slow SaaS dashboards by magic.
- Use foreign keys and enable `PRAGMA foreign_keys = ON`.
  Reason: app bugs should not silently create orphaned data.
- Wrap multi-step writes in transactions.
  Reason: subscription, membership, and quota updates must not half-succeed.
- Use parameterized queries through Drizzle. Never concatenate user input into SQL.
  Reason: SQL injection remains possible in SQLite.
- Store timestamps as ISO 8601 UTC text unless an existing schema uses integers.
  Reason: ISO text is debuggable and sorts correctly when normalized.
- Soft-delete user-owned SaaS records with `deleted_at`; hard-delete short-lived tokens and sessions.
  Reason: users need recovery and audits, but security artifacts should expire cleanly.

## Component Patterns

- Use Server Components for pages, layouts, and data-fetching shells.
  Reason: database queries stay server-side and bundle size stays smaller.
- Use Client Components only for stateful interaction, browser APIs, optimistic UI, and controlled forms.
  Reason: client boundaries should be deliberate and easy to review.
- Keep forms as small Client Components that call server actions.
  Reason: validation and writes stay on the server while the browser handles input state.
- Validate form input with Zod before any service call.
  Reason: services should receive trusted shapes, not raw `FormData`.
- Return typed action results, not thrown strings.
  Reason: UI can show field errors, toast messages, and retry states consistently.
- Use `loading.tsx`, `error.tsx`, and empty states for every dashboard route that fetches data.
  Reason: SaaS users spend most time in dashboard states that are not happy paths.
- Keep cards, tables, and forms dense and scannable.
  Reason: SaaS interfaces are work surfaces, not landing pages.
- Prefer accessible native controls before custom widgets.
  Reason: keyboard support and screen reader behavior should be boring and reliable.

## Patterns To Follow

- Start with the database model, then service, then action/route, then UI.
  Reason: SaaS behavior is usually data ownership and permissions first.
- Check authorization inside services, not only in pages.
  Reason: routes, actions, jobs, and future APIs must share the same guardrails.
- Pass `userId` or `accountId` explicitly into services.
  Reason: hidden globals make tests and permission reviews brittle.
- Keep route handlers thin: parse request, call service, return response.
  Reason: handlers should be transport glue, not business logic.
- Centralize error mapping in `src/lib/errors.ts`.
  Reason: users need safe messages while logs keep details.
- Use feature flags or config values through typed env access.
  Reason: stringly typed `process.env` reads spread risk through the codebase.
- Add tests for every permission branch and every destructive mutation.
  Reason: SaaS failures usually involve access control, not simple rendering.
- Prefer simple tables before event sourcing or complex state machines.
  Reason: SQLite SaaS apps should stay legible until complexity proves itself.

## What We Don't Do (And Why)

- Do not put database clients or secrets in Client Components.
  Reason: they can leak into browser bundles or encourage unsafe fetch patterns.
- Do not use API routes as an internal layer for Server Components.
  Reason: Server Components can call services directly without an HTTP hop.
- Do not create generic `utils.ts` dumping grounds.
  Reason: vague files become unowned and hard to review.
- Do not add global state libraries for server data.
  Reason: App Router and Server Components already model server state.
- Do not hand-roll auth crypto.
  Reason: session security is easy to get subtly wrong.
- Do not write migrations that depend on current application code.
  Reason: old migrations must run after the app has changed.
- Do not swallow errors with `catch {}`.
  Reason: silent failures make billing, auth, and data loss impossible to debug.
- Do not add decorative landing-page patterns to the product dashboard.
  Reason: SaaS dashboards need speed, hierarchy, and repeatable scanning.
- Do not introduce background jobs without idempotency keys.
  Reason: retries must not double-send emails, invoices, or webhooks.
- Do not ask the user to choose defaults already specified here.
  Reason: this file exists so Claude Code can proceed with a coherent opinion.

## Greenfield Bootstrap Checklist

1. Create Next.js 15 with TypeScript, App Router, Tailwind, and `src/`.
2. Add Drizzle, `better-sqlite3`, Zod, Vitest, and Playwright.
3. Create `src/lib/env.ts` with validated environment variables.
4. Create `src/db/client.ts`, `src/db/schema`, and migration scripts.
5. Add auth session tables before building private dashboard routes.
6. Build one vertical slice: schema, service, action, form, page, tests.
7. Run `pnpm lint`, `pnpm typecheck`, `pnpm test`, and `pnpm build`.

## Default Environment Variables

```text
DATABASE_URL=file:./data/dev.sqlite
SESSION_SECRET=replace-with-32-byte-secret
APP_URL=http://localhost:3000
```

For Turso deployments, use `TURSO_DATABASE_URL` and `TURSO_AUTH_TOKEN`, but keep local development on file-backed SQLite unless production parity requires otherwise.

## Response Style For Claude Code

- State the assumed stack once, then implement.
- If a requested change conflicts with this guide, explain the conflict and choose the safer path.
- When touching data writes, mention migration and permission impacts.
- When adding UI, include loading, empty, and error states.
- Before finishing, report the commands run and any commands that could not run.
