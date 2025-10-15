# aiogram-template

This is a template for creating Telegram bots using the aiogram library.

#### ❗️ Read [HELP.md](HELP.md) if something is unclear ❗️

### Template uses:

* SQLAlchemy + Alembic
* PostgreSQL
* Redis
* Caddy Server
* Docker
* i18n (Project Fluent)
* uv

***

## Installation

### Step 1: Clone the repository

```shell
git clone https://github.com/andrew000/aiogram-template.git
cd aiogram-template
```

### Step 2: Install dependencies

I recommend using [UV](https://docs.astral.sh/uv/) to manage your project.

```shell
# Create virtual environment using UV
uv venv --python=3.13

# Install dependencies
make sync
```

### Step 3: Create `.env` file

Create a `.env` file in the root of the project and fill it with the necessary data.

```shell
cp .env.example .env.docker # for docker development
cp .env.example .env # for local development
```

### Step 4: Deploy project

```shell
make up
```

### Step 5: Run migrations

Template already has initial migration. To apply it, run the following command:

```shell
make upgrade-revision revision=head
```

### Step 6: Bot is ready and running

Bot is ready to use. You can check the logs using the following command:

```shell
docker compose logs -f
```

***

## Explanation

### Project structure

The project structure is as follows:

```
AIOGRAM-TEMPLATE
├───app (main application)
│   ├───bot (bot)
│   ├───migrations (alembic migrations)
├───├───pyproject.toml (application configuration)
│   ├───Dockerfile-bot (Dockerfile for the bot)
│   └───Dockerfile-migrations (Dockerfile for the migrations)
├───caddy (Caddy web server)
├───psql (PostgreSQL database)
│   ├───data (database data)
│   └───db-init-script (database initialization script)
├───redis (Redis database)
│   └───data (redis data)
├───pyproject.toml (project configuration)
├───docker-compose.yml (docker-compose configuration)
├───.env.example (example environment file)
├───.pre-commit-config.yaml (pre-commit configuration)
└───Makefile (make commands)
```

The bot is located in the `app/bot` directory. The bot is divided into modules, each of which is responsible for a
specific functionality. `handlers` are responsible for processing events, `middlewares` for preprocessing events,
`storages` for declaring models and working with the database, `locales` for localization, `filters` for own filters,
`errors` for error handling.

### Migrations

Migration files are located in the `app/migrations` directory.

❗️ It is recommended to create migrations files before you push your code to the repository.

❗️ Always check your migrations before apply them to the production database.

To create initial migration, check if your models imported in the `app/bot/storages/psql/__init__.py` file and run the
following command:

```shell
make create-init-revision
```

To apply `head` migration, run the following command:
```shell
make upgrade-revision revision=head
```

To apply specific migration, run the following command:

```shell
make upgrade-revision revision=<revision_id>
```

`revision_id` - id of the migration in the `app/migrations/versions` directory. Initial migration id is
`000000000000`.

To check current migration `revision_id` in the database, run the following command:

```shell
make current-revision
```

### Localization

The Bot supports localization. Localization files are located in the `app/bot/locales` directory. The bot uses the
`aiogram-i18n` library for localization and `FTL-Extract` for extracting FTL-keys from the code.

To extract FTL-keys from the code, run the following command:

```shell
make extract-locales
```

After extracting FTL-keys, you can find new directories and files in the `app/bot/locales` directory. To add or remove
locales for extraction, edit `Makefile`

I recommend to make a submodule from `app/bot/locales` directory. It will allow you to control locales versions and
publish them (without code exposing) for translations help by other people.

### Pre-commit

The project uses pre-commit hooks. To install pre-commit hooks, run the following command:

```shell
uv run pre-commit install
```

### Docker

The project uses Docker for deployment. To build and run the bot in Docker, run the following command:

```shell
make up
```

Yes, little command to run large project. It will build and run the bot, PostgreSQL, Redis, and Caddy containers.

To gracefully stop the bot and remove containers, run the following command:

```shell
make down
```

### Caddy

The project uses Caddy as a web server. Caddy can automatically get and renew SSL certificates. To configure Caddy, edit
the `Caddyfile` file in the `caddy` directory. `public` directory is used to store static files.

By default, Caddy is disabled in the `docker-compose.yml` file. To enable Caddy, uncomment the `caddy` service in the
`docker-compose.yml` file.

### Webhooks

Bot may use webhooks. To enable webhooks, set `WEBHOOKS` environment variable to `True` in the `.env` file. Also, set
`WEBHOOK_URL` and `WEBHOOK_SECRET_TOKEN` environment variables.

Don't forget to uncomment the `caddy` service in the `docker-compose.yml` file.
