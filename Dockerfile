FROM apachesuperset.docker.scarf.sh/apache/superset:3.1.0

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

COPY --chown=superset ./superset_config.py /app

USER superset
