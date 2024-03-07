FROM apachesuperset.docker.scarf.sh/apache/superset

ENV SUPERSET_CONFIG_PATH /app/superset_config.py

COPY --chown=superset ./superset_config.py /app
