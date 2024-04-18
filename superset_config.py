import os
from datetime import timedelta

from celery.schedules import crontab
from flask_appbuilder.security.manager import AUTH_DB
from flask_caching.backends.rediscache import RedisCache
from superset.tasks.types import ExecutorType

ENABLE_PROXY_FIX = True

FEATURE_FLAGS = {
    "ALERT_REPORTS": True,
    "TAGGING_SYSTEM": True,
}

ROW_LIMIT = 300_000

PREVIOUS_SECRET_KEY = "thisISaSECRET_1234"  # gitleaks:allow

SECRET_KEY = os.environ.get("SECRET_KEY")

DATABASE_USERNAME = os.environ.get("POSTGRESQL_USERNAME")

DATABASE_PASSWORD = os.environ.get("POSTGRESQL_PASSWORD")

SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@superset-postgresql:5432/superset"


# Authlib

AUTH_TYPE = AUTH_DB

AZURE_TENANT_ID = os.environ.get("AZURE_TENANT_ID")

OAUTH_PROVIDERS = [
    {
        "name": "azure",
        "icon": "fa-windows",
        "token_key": "access_token",
        "remote_app": {
            "client_id": os.environ.get("AZURE_CLIENT_ID"),
            "client_secret": os.environ.get("AZURE_CLIENT_SECRET"),
            "api_base_url": f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/oauth2",
            "client_kwargs": {
                "scope": "User.read name preferred_username email profile upn",
                "resource": os.environ.get("AZURE_CLIENT_ID"),
                "verify_signature": False,
            },
            "request_token_url": None,
            "access_token_url": f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/oauth2/token",
            "authorize_url": f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/oauth2/authorize",
        },
    },
    {
        "name": "google",
        "icon": "fa-google",
        "token_key": "access_token",
        "remote_app": {
            "client_id": os.environ.get("GOOGLE_KEY"),
            "client_secret": os.environ.get("GOOGLE_SECRET"),
            "api_base_url": "https://www.googleapis.com/oauth2/v2/",
            "client_kwargs": {"scope": "email profile"},
            "request_token_url": None,
            "access_token_url": "https://accounts.google.com/o/oauth2/token",
            "authorize_url": "https://accounts.google.com/o/oauth2/auth",
            "authorize_params": {"hd": os.environ.get("OAUTH_HOME_DOMAIN", "")},
        },
    },
]

AUTH_ROLE_ADMIN = "Admin"

AUTH_ROLE_PUBLIC = "Public"

AUTH_USER_REGISTRATION = True

AUTH_USER_REGISTRATION_ROLE = "Gamma"


# Flask-WTF

WTF_CSRF_ENABLED = False

WTF_CSRF_EXEMPT_LIST = []

WTF_CSRF_TIME_LIMIT = int(timedelta(days=365).total_seconds())


# Session cookie

SESSION_COOKIE_SAMESITE = "Strict"

SESSION_COOKIE_SECURE = True

SESSION_COOKIE_HTTPONLY = True


# Redis

REDIS_HOST = os.environ.get("REDIS_HOST", "superset-redis-headless")

REDIS_PORT = os.environ.get("REDIS_PORT", 6379)

REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"


# Celery


class CeleryConfig:
    broker_url = REDIS_URL
    result_backend = REDIS_URL
    worker_log_level = "DEBUG"
    worker_prefetch_multiplier = 10
    task_acks_late = True
    imports = (
        "superset.sql_lab",
        "superset.tasks.scheduler",
        "superset.tasks.cache",
    )
    task_annotations = {
        "sql_lab.get_sql_results": {
            "rate_limit": "100/s",
        },
    }
    beat_schedule = {
        "reports.scheduler": {
            "task": "reports.scheduler",
            "schedule": crontab(minute="*", hour="*"),
        },
        "cache-warmup-hourly": {
            "task": "cache-warmup",
            "schedule": crontab(minute="5,15,25,45,55", hour="*"),
            "kwargs": {
                "strategy_name": "dashboard_tags",
                "tags": ["active"],
            },
        },
    }


CELERY_CONFIG = CeleryConfig

DATA_CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_KEY_PREFIX": "superset_results",
    "CACHE_DEFAULT_TIMEOUT": int(timedelta(hours=12).total_seconds()),
    "CACHE_REDIS_URL": REDIS_URL,
}

RESULTS_BACKEND = RedisCache(
    host=REDIS_HOST,
    port=REDIS_PORT,
    key_prefix="superset_results",
)

# Talisman

TALISMAN_ENABLED = True

TALISMAN_CONFIG = {
    "force_https": True,
    "force_https_permanent": True,
    "frame_options": "SAMEORIGIN",
    "strict_transport_security_preload": True,
    "strict_transport_security_max_age": int(timedelta(days=365).total_seconds()),
    "strict_transport_security_include_subdomains": True,
    "content_security_policy": {
        "default-src": "'self'",
        "img-src": ["*", "data:", "blob:"],
        "media-src": "*",
        "style-src": ["'self'", "'unsafe-inline'"],
        "script-src": ["'self'", "'strict-dynamic'"],
    },
    "content_security_policy_nonce_in": ["script-src"],
    "session_cookie_secure": True,
    "session_cookie_http_only": True,
}


# Misc

SUPERSET_WEBSERVER_TIMEOUT = int(timedelta(minutes=2).total_seconds())

SQLLAB_ASYNC_TIME_LIMIT_SEC = int(timedelta(hours=1).total_seconds())

SQLLAB_TIMEOUT = int(timedelta(minutes=2).total_seconds())

SLACK_API_TOKEN = os.environ.get("SLACK_API_TOKEN")

WEBDRIVER_BASEURL = "http://superset:8088/"

WEBDRIVER_BASEURL_USER_FRIENDLY = WEBDRIVER_BASEURL

THUMBNAIL_SELENIUM_USER = "admin"

ALERT_REPORTS_EXECUTE_AS = [ExecutorType.SELENIUM]
