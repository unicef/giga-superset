FROM apachesuperset.docker.scarf.sh/apache/superset:3.1.0

ENV SUPERSET_CONFIG_PATH /app/superset_config.py

COPY --chown=superset ./superset_config.py /app
