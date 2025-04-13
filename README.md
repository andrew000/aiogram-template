# aiogram-template

This is a template for creating Telegram bots using the aiogram library.

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

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
make sync
```

### Step 3: Create `.env` file

Create a `.env` file in the root of the project and fill it with the necessary data.

```shell
cp .env.example .env
```

### Step 4: Run the bot in Docker

```shell
make up
```

***

## Explanation

### Project structure

The project structure is as follows:

```
AIOGRAM-TEMPLATE
├───app (main application)
│   ├───bot (bot)
│   │   ├───Dockerfile (Dockerfile for the bot)
│   ├───migrations (alembic migrations)
├───caddy (Caddy web server)
├───psql (PostgreSQL database)
│   ├───data (database data)
│   └───db-init-script (database initialization script)
├───redis (Redis database)
│   └───data (redis data)
├───pyproject.toml (project configuration)
├───.env.example (example environment file)
├───docker-compose.yml (docker-compose configuration)
├───.pre-commit-config.yaml (pre-commit configuration)
└───Makefile (make commands)
```

The bot is located in the `app/bot` directory. The bot is divided into modules, each of which is responsible for a
specific functionality. `handlers` are responsible for processing events, `middlewares` for preprocessing events,
`storages` for declaring models and working with the database, `locales` for localization, `filters` for own filters,
`errors` for error handling.

### Migrations

Migration files are located in the `app/migrations` directory.

I hate when app makes migrations automatically. It often causes problems. So I prefer to create and upgrade migrations
manually. Additionally, I always add function, to compare in-code `migration_rev_id` with database `migration_rev_id`
(function is not included in template). If they are different, the app will raise an error and exit.

To create initial migration, check if your models imported in the `app/bot/storages/psql/__init__.py` file and run the
following command (Don't forget to run database container):

Command will create initial migration file in the `app/migrations/versions` directory and create an empty table
`alembic_version` in the database.

```shell
make create-init-revision
```

To apply the migration, run the following command:

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

The bot supports localization. Localization files are located in the `app/bot/locales` directory. The bot uses the
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

***

## FAQ

**Q:** Why PyCharm marks import with red color?

**A:** I use "unique" project structure, where `app` directory contains code, but root directory contains configuration
files.

In PyCharm, right-click on the `app` directory and select `Mark Directory as` -> `Sources Root`. Also,
**unmark** project root directory `Unmark as Sources Root`. This will fix the problem.

![image](https://github.com/user-attachments/assets/d424facd-342d-4215-b05d-0529d2273d28)

![image](https://github.com/user-attachments/assets/f5030c90-320d-4a3a-a11a-97175a1a447a)

![image](https://github.com/user-attachments/assets/9cca557a-3607-4019-9e94-4f4ffba86211)

***

**Q:** Why You import `sys` or `os` libs
like [this](https://github.com/andrew000/aiogram-template/blob/6052d9bd2cbb9332620f5996bf6065a0b918d3bf/app/bot/__main__.py#L140)?

**A:** _My inclinations make me do this to avoid some attack vector invented by my paranoia_
***

**Q:** Why not use `aiogram-cli`?

**A:** _It's a good library, but I prefer to use my own code 🤷‍♂️_
***

## Useful commands

#### Update Dependencies

First, run `make outdated` to check for outdated dependencies. Then, edit `pyproject.toml` file and run the
following command to update dependencies:

```shell
make outdated

# Edit pyproject.toml

uv lock --upgrade
make sync
```

#### Check Dependencies Updates

```shell
make outdated
```

#### Linting

```shell
make lint
```

#### MyPy

```shell
make mypy
```

#### Formatting

```shell
make format
```
