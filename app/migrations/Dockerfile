FROM python:3.14.3-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

ARG USER_ID=${USER_ID:-999}
ARG GROUP_ID=${GROUP_ID:-999}
ARG USER_NAME=${USER_NAME:-migrator}

WORKDIR /app

RUN if [ "$USER_NAME" != "root" ]; then \
      echo "Creating non-root user: $USER_NAME" && \
      groupadd --system --gid=${GROUP_ID} ${USER_NAME} && \
      useradd --system --shell /bin/false --no-log-init --gid=${GROUP_ID} --uid=${USER_ID} ${USER_NAME} && \
      chown ${USER_NAME}:${USER_NAME} /app ; \
    else \
      echo "Running as root, skipping user creation"; \
    fi

USER ${USER_NAME}

COPY --chown=${USER_NAME}:${USER_NAME} pyproject.toml /app/

RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    uv --no-cache sync --no-dev

COPY --chown=${USER_NAME}:${USER_NAME} . /app/
