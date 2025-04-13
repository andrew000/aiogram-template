FROM python:3.13.3-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

ARG USER_ID=999
ARG GROUP_ID=999
ARG USER_NAME=bot

WORKDIR /app

RUN groupadd --system --gid=${GROUP_ID} ${USER_NAME} && \
    useradd --system --shell /bin/false --no-log-init --gid=${GROUP_ID} --uid=${USER_ID} ${USER_NAME} && \
    chown ${USER_NAME}:${USER_NAME} /app

COPY --chown=${USER_NAME}:${USER_NAME} pyproject.toml /app/

RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    uv sync --no-dev && \
    uv pip uninstall --system pip wheel

COPY --chown=${USER_NAME}:${USER_NAME} . /app/
