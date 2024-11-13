include .env
export

app-dir = app
bot-dir = bot

.PHONY up:
up:
	docker compose -f docker-compose.yml up -d --build --timeout 60

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
	uv run mypy --config-file pyproject.toml --package $(app-dir).$(bot-dir)

.PHONY outdated:
outdated:
	uv tree --outdated --universal

.PHONY sync:
sync:
	uv sync --extra dev --extra lint --extra uvloop --link-mode=copy

.PHONY freeze: sync
freeze:
	uv export --quiet --format requirements-txt --no-dev --extra uvloop --output-file $(app-dir)\requirements.txt

.PHONY create-revision:
create-revision:
	cd $(app-dir) && uv run alembic revision --autogenerate -m "$(message)"

.PHONY upgrade-revision:
upgrade-revision:
	cd $(app-dir) && uv run alembic upgrade "$(revision)"

.PHONY downgrade-revision:
downgrade-revision:
	cd $(app-dir) && uv run alembic downgrade "$(revision)"

.PHONY current-revision:
current-revision:
	cd $(app-dir) && uv run alembic current

.PHONY create-init-revision:
create-init-revision:
	cd $(app-dir) && uv run alembic revision --autogenerate -m 'Initial' --rev-id 000000000000
