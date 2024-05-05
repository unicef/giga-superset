FROM apache/superset:3.1.0

ENV SUPERSET_CONFIG_PATH /app/superset_config.py
ENV GECKODRIVER_VERSION 0.29.0

USER root

RUN apt-get update && \
    apt-get install --no-install-recommends -y wget firefox-esr && \
    wget -q https://github.com/mozilla/geckodriver/releases/download/v${GECKODRIVER_VERSION}/geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz && \
    tar -x geckodriver -zf geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz -O > /usr/bin/geckodriver && \
    chmod 755 /usr/bin/geckodriver && \
    rm geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
      "authlib==1.3.0" \
      "trino[sqlalchemy]==0.328.0" \
      "psycopg2-binary==2.9.9" \
      "redis==4.6.0" \
      "gevent==24.2.1"

COPY --chown=superset ./superset_config.py /app

USER superset
