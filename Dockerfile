FROM python:3.11-alpine3.19 as deps

ARG POETRY_VERSION=1.7.1

WORKDIR /tmp

COPY pyproject.toml poetry.lock ./

RUN apk add --no-cache curl && \
    curl -sSL https://install.python-poetry.org | python - && \
    poetry export --without-hashes --without dev -f requirements.txt > requirements.txt

FROM apachesuperset.docker.scarf.sh/apache/superset

ENV SUPERSET_CONFIG_PATH /app/superset_config.py

COPY --chown=superset ./superset_config.py /app
COPY --from=deps --chown=superset /tmp/requirements.txt /app

RUN pip install --no-cache-dir -r /app/requirements.txt
