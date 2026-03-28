# Copilot Instructions for aiogram-template

## Project overview
- This repository is an aiogram 3 Telegram bot template with a workspace layout managed by `uv`.
- Main app code is in `app/bot`.
- Database migrations are in `app/migrations` (Alembic).
- Infrastructure is containerized via `docker-compose.yml` (bot, migrations, PostgreSQL, Redis, optional Caddy).

## Tech stack
- Python 3.14
- aiogram 3
- SQLAlchemy + Alembic
- PostgreSQL + Redis
- i18n with Project Fluent (`app/bot/locales`)
- Tooling: `uv`, `just`, `ruff`, `isort`, `mypy`, `pre-commit`

## Repository structure conventions
- Put bot logic under `app/bot` modules:
  - `handlers` for Telegram event handlers
  - `middlewares` for middleware
  - `filters` for custom filters
  - `errors` for error handlers
  - `storages` for DB/cache-related logic and models
  - `utils` for shared utilities
  - `settings.py` for configuration
  - `main.py` as bot entrypoint
- Keep migration changes in `app/migrations/versions` and ensure models are imported where Alembic autogenerate can detect them.

## Coding guidelines
- Follow existing project style and keep edits minimal/surgical.
- Prefer explicit typing; keep `mypy` compatibility in mind.
- Keep line length within 100 chars.
- Use double quotes in Python strings (project formatter convention).
- Do not introduce new frameworks or major architectural changes unless requested.

## Localization (FTL)
- User-facing strings should be localizable through Fluent where applicable.
- Locale files are in `app/bot/locales`.
- Regenerate extracted localization keys when needed:
  - `just extract-locales`
  - `just stub`
- Check missing translations before finishing localization-related changes:
  - `just untranslated`

## Quality checks
Run relevant checks after code changes:
- Lint: `just lint`
- Type check: `just mypy`
- Format (when needed): `just format`

## Dependency and environment workflow
- Use `uv` for dependency management.
- Sync environment with: `just sync`
- For dependency updates, use `just outdated`, then `uv lock --upgrade`, then `just sync`.

## Runtime and DB workflow
- Start services: `just up` (or `just up-db` for database/redis only)
- Stop services: `just down`
- Migrations:
  - Create: `just create-revision "<message>"`
  - Upgrade: `just upgrade-revision head`
  - Check current: `just current-revision`

## Pull request / change expectations
- Keep PRs focused and avoid unrelated refactors.
- Update docs only when behavior or workflow changes.
- Avoid committing secrets or `.env` values.

## Agent-specific instructions
- When adding features, first locate and follow existing patterns in nearby modules.
- Reuse existing helpers/utilities before introducing new ones.
- If adding DB models/fields, include an Alembic migration.
- If adding user-visible text, update locale resources accordingly.
