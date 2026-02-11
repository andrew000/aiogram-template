set shell := ["bash", "-c"]
set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

app-dir := "app"
bot-dir := "bot"

[windows]
up:
    docker compose \
      --env-file .env \
      --file docker-compose.yml \
      up \
      -d \
      --build \
      --timeout 60 \
      bot

[unix]
up:
    docker compose \
      --env-file .env \
      --file docker-compose.yml \
      build \
      --build-arg USER_ID=$(id -u) \
      --build-arg GROUP_ID=$(id -g) \
      --build-arg USER_NAME=$(whoami) \
      bot

    docker compose \
      --env-file .env \
      --file docker-compose.yml \
      up \
      -d \
      --timeout 60 \
      bot

[windows]
up-db:
    docker compose \
      --env-file .env \
      --file docker-compose.yml \
      up \
      -d \
      --build \
      --timeout 60 \
      database redis

[unix]
up-db:
    docker compose \
      --env-file .env \
      --file docker-compose.yml \
      build \
      --build-arg USER_ID=$(id -u) \
      --build-arg GROUP_ID=$(id -g) \
      --build-arg USER_NAME=$(whoami) \
      database redis

    docker compose \
      --env-file .env \
      --file docker-compose.yml \
      up \
      -d \
      --timeout 60 \
      database redis

[windows]
build:
    docker compose \
      --env-file .env \
      --file docker-compose.yml \
      build \
      bot migrations

[unix]
build:
    docker compose \
      --env-file .env \
      --file docker-compose.yml \
      build \
      --build-arg USER_ID=$(id -u) \
      --build-arg GROUP_ID=$(id -g) \
      --build-arg USER_NAME=$(whoami) \
      bot migrations

down:
    docker compose \
      --env-file .env \
      --file docker-compose.yml \
      down \
      --timeout 60

pull:
    git pull origin master
    git submodule update --init --recursive

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

stub:
    uv run ftl stub \
      './app/bot/locales/en' \
      './app/bot'

lint:
    echo "Running ruff..."
    uv run ruff check {{ app-dir }} --show-fixes --preview

format:
    echo "Running ruff check with --fix..."
    uv run ruff check {{ app-dir }} --fix --unsafe-fixes

    echo "Running ruff..."
    uv run ruff format {{ app-dir }}

    echo "Running isort..."
    uv run isort {{ app-dir }}

mypy:
    echo "Running MyPy..."
    uv run mypy --explicit-package-bases {{ app-dir }}/{{ bot-dir }}

outdated:
    uv tree --universal --outdated --depth 2

sync:
    uv sync --all-extras

create-revision message: build
    docker compose \
        --env-file .env \
        --file docker-compose.yml \
        run \
        --rm \
        migrations \
        bash -c ".venv/bin/alembic --config alembic.ini revision --autogenerate -m '{{ message }}'"

upgrade-revision revision: build
    docker compose \
        --env-file .env \
        --file docker-compose.yml \
        run \
        --rm \
        migrations \
        bash -c ".venv/bin/alembic --config alembic.ini upgrade {{ revision }}"

downgrade-revision revision: build
    docker compose \
        --env-file .env \
        --file docker-compose.yml \
        run \
        --rm \
        migrations \
        bash -c ".venv/bin/alembic --config alembic.ini downgrade {{ revision }}"

current-revision: build
    docker compose \
        --env-file .env \
        --file docker-compose.yml \
        run \
        --rm \
        migrations \
        bash -c ".venv/bin/alembic --config alembic.ini current"

create-init-revision: build
    docker compose \
        --env-file .env \
        --file docker-compose.yml \
        run \
        --rm \
        migrations \
        bash -c ".venv/bin/alembic --config alembic.ini revision --autogenerate -m 'Initial' --rev-id 000000000000"
