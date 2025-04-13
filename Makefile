include .env
export

app-dir = app
bot-dir = bot

.PHONY up:
up:
	docker compose -f docker-compose.yml up -d --build --timeout 60 bot

.PHONY down:
down:
	docker compose -f docker-compose.yml down --timeout 60

.PHONY pull:
pull:
	git pull origin master
	git submodule update --init --recursive

.PHONY extract-locales:
extract-locales:
	uv run ftl_extract \
	'.\app\bot' \
	'.\app\bot\locales' \
	-l 'en' \
	-l 'uk' \
	-k 'i18n' \
	-k 'L' \
	-k 'LF' \
	-k 'LazyProxy' \
	-a 'core' \
	--comment-junks

.PHONY lint:
lint:
	echo "Running ruff..."
	uv run ruff check --config pyproject.toml --diff $(app-dir)

.PHONY format:
format:
	echo "Running ruff check with --fix..."
	uv run ruff check --config pyproject.toml --fix --unsafe-fixes $(app-dir)

	echo "Running ruff..."
	uv run ruff format --config pyproject.toml $(app-dir)

	echo "Running isort..."
	uv run isort --settings-file pyproject.toml $(app-dir)

.PHONE mypy:
mypy:
	echo "Running MyPy..."
	uv run mypy --config-file pyproject.toml --explicit-package-bases $(app-dir)/$(bot-dir)

.PHONY outdated:
outdated:
	uv tree --outdated --universal

.PHONY sync:
sync:
	uv sync --extra dev --extra lint --link-mode=copy

.PHONY create-revision:
create-revision:
	docker compose run --build --rm --user migrator migrations bash -c ".venv/bin/alembic --config alembic.ini revision --autogenerate -m '$(message)'"

.PHONY upgrade-revision:
upgrade-revision:
	docker compose run --build --rm --user migrator migrations bash -c ".venv/bin/alembic --config alembic.ini upgrade $(revision)"

.PHONY downgrade-revision:
downgrade-revision:
	docker compose run --build --rm --user migrator migrations bash -c ".venv/bin/alembic --config alembic.ini downgrade $(revision)"

.PHONY current-revision:
current-revision:
	docker compose run --build --rm --user migrator migrations bash -c ".venv/bin/alembic --config alembic.ini current"

.PHONY create-init-revision:
create-init-revision:
	docker compose run --build --rm --user migrator migrations bash -c ".venv/bin/alembic --config alembic.ini revision --autogenerate -m 'Initial' --rev-id 000000000000"
