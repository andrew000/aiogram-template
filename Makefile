include .env
export

ifeq ($(OS),Windows_NT)
    DETECTED_OS := Windows
else
    DETECTED_OS := $(shell uname -s)
endif

app-dir = app
bot-dir = bot

.PHONY: up
up:
ifeq ($(DETECTED_OS),Windows)
	docker compose \
		--env-file .env.docker \
		--file docker-compose.yml \
		up \
		-d \
		--build \
		--timeout 60 \
		bot controller
else
	docker compose \
		--env-file .env.docker \
		--file docker-compose.yml \
		build \
		--build-arg USER_ID=$(SUDO_UID) \
		--build-arg GROUP_ID=$(SUDO_GID) \
		--build-arg USER_NAME=$(SUDO_USER) \
		bot controller

	docker compose \
		--env-file .env.docker \
		--file docker-compose.yml \
		up \
		-d \
		--timeout 60 \
		bot controller
endif

.PHONY: up-db
up-db:
	docker compose \
		--env-file .env.docker \
		--file docker-compose.yml \
		up \
		-d \
		--build \
		--timeout 60 \
		database redis
endif

.PHONY: build
build:
ifeq ($(DETECTED_OS),Windows)
	docker compose \
		--env-file .env.docker \
		--file docker-compose.yml \
		up \
		-d \
		--build \
		--timeout 60 \
		bot migrations
else
	docker compose \
		--env-file .env.docker \
		--file docker-compose.yml \
		build \
		--build-arg USER_ID=$(SUDO_UID) \
		--build-arg GROUP_ID=$(SUDO_GID) \
		--build-arg USER_NAME=$(SUDO_USER) \
		bot migrations
endif

.PHONY: down
down:
	docker compose --env-file .env.docker --file docker-compose.yml down --timeout 60

.PHONY: pull
pull:
	git pull origin master
	git submodule update --init --recursive

.PHONY: extract-locales
extract-locales:
	uv run fast-ftl-extract \
	'./app/bot' \
	'./app/bot/locales' \
	-l 'en' \
	-l 'uk' \
	-K 'LF' \
	-I 'core' \
	--comment-junks \
	--comment-keys-mode 'comment' \
	--verbose

.PHONY: stub
stub:
	uv run ftl stub \
	'./app/bot/locales/en' \
	'./app/bot'

.PHONY: lint
lint:
	echo "Running ruff..."
	uv run ruff check --config pyproject.toml --diff $(app-dir)

.PHONY: format
format:
	echo "Running ruff check with --fix..."
	uv run ruff check --config pyproject.toml --fix --unsafe-fixes $(app-dir)

	echo "Running ruff..."
	uv run ruff format --config pyproject.toml $(app-dir)

	echo "Running isort..."
	uv run isort --settings-file pyproject.toml $(app-dir)

.PHONY: mypy
mypy:
	echo "Running MyPy..."
	uv run mypy --config-file pyproject.toml --explicit-package-bases $(app-dir)/$(bot-dir)

.PHONY: outdated
outdated:
	uv tree --outdated --universal

.PHONY: sync
sync:
	uv sync --extra dev --extra lint

.PHONY: create-revision
create-revision: build
	docker compose \
		--env-file .env.docker \
		--file docker-compose.yml \
		run \
		--rm \
		migrations \
		bash -c ".venv/bin/alembic --config alembic.ini revision --autogenerate -m '$(message)'"

.PHONY: upgrade-revision
upgrade-revision: build
	docker compose \
		--env-file .env.docker \
		--file docker-compose.yml \
		run \
		--rm \
		migrations \
		bash -c ".venv/bin/alembic --config alembic.ini upgrade $(revision)"

.PHONY: downgrade-revision
downgrade-revision: build
	docker compose \
		--env-file .env.docker \
		--file docker-compose.yml \
		run \
		--rm \
		migrations \
		bash -c ".venv/bin/alembic --config alembic.ini downgrade $(revision)"

.PHONY: current-revision
current-revision: build
	docker compose \
		--env-file .env.docker \
		--file docker-compose.yml \
		run \
		--rm \
		migrations \
		bash -c ".venv/bin/alembic --config alembic.ini current"

.PHONY: create-init-revision
create-init-revision: build
	docker compose \
		--env-file .env.docker \
		--file docker-compose.yml \
		run \
		--rm \
		migrations \
		bash -c ".venv/bin/alembic --config alembic.ini revision --autogenerate -m 'Initial' --rev-id 000000000000"
