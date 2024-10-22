import logging
import os
from datetime import timedelta
from typing import Any

from celery.schedules import crontab
from flask_appbuilder.const import AUTH_DB, AUTH_OAUTH
from flask_caching.backends.rediscache import RedisCache
from superset import SupersetSecurityManager
from superset.tasks.types import ExecutorType

logger = logging.getLogger(__name__)

ENABLE_PROXY_FIX = True

FEATURE_FLAGS = {
    "ALERT_REPORTS": True,
    "TAGGING_SYSTEM": True,
}

ROW_LIMIT = 300_000


PREVIOUS_SECRET_KEY = "thisISaSECRET_1234"  # gitleaks:allow

SECRET_KEY = os.environ.get("SECRET_KEY")

DEPLOY_ENV = os.environ.get("DEPLOY_ENV")

DATABASE_USERNAME = os.environ.get("POSTGRESQL_USERNAME")

DATABASE_PASSWORD = os.environ.get("POSTGRESQL_PASSWORD")

DATABASE_NAME = os.environ.get("POSTGRESQL_DATABASE")


# SQLAlchemy

SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@superset-postgresql:5432/{DATABASE_NAME}"

SQLALCHEMY_POOL_SIZE = 20

SQLALCHEMY_MAX_OVERFLOW = 15

SQLALCHEMY_POOL_TIMEOUT = 300


# Authlib

AUTH_TYPE = AUTH_DB if DEPLOY_ENV == "stg" else AUTH_OAUTH

AZURE_CLIENT_ID = os.environ.get("AZURE_CLIENT_ID")
AZURE_CLIENT_SECRET = os.environ.get("AZURE_CLIENT_SECRET")
AZURE_TENANT_ID = os.environ.get("AZURE_TENANT_ID")
AZURE_TENANT_NAME = os.environ.get("AZURE_TENANT_NAME")
AZURE_POLICY_NAME = os.environ.get("AZURE_POLICY_NAME")

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")

OAUTH_PROVIDERS = [
    {
        "name": "azure",
        "icon": "fa-windows",
        "token_key": "access_token",
        "remote_app": {
            "client_id": AZURE_CLIENT_ID,
            "client_secret": AZURE_CLIENT_SECRET,
            "server_metadata_url": f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/.well-known/openid-configuration",
            "client_kwargs": {
                "scope": "openid profile offline_access User.Read",
                "resource": AZURE_CLIENT_ID,
            },
        },
    },
    {
        "name": "google",
        "icon": "fa-google",
        "token_key": "access_token",
        "remote_app": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
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

AUTH_ROLES_SYNC_AT_LOGIN = False


class CustomSsoSecurityManager(SupersetSecurityManager):
    def get_oauth_user_info(
        self,
        provider: str,
        resp: dict[str, Any],
    ) -> dict[str, Any]:
        if provider == "azure":
            me = self._decode_and_validate_azure_jwt(resp["id_token"])
            logger.debug("User info from Azure: %s", me)
            return {
                "email": me["email"],
                "first_name": me.get("given_name", ""),
                "last_name": me.get("family_name", ""),
                "username": me["email"],
                "role_keys": me.get("groups", []),
            }
        else:
            return super().get_oauth_user_info(provider, resp)


# CUSTOM_SECURITY_MANAGER = CustomSsoSecurityManager


# Flask-WTF

WTF_CSRF_ENABLED = False

WTF_CSRF_EXEMPT_LIST = []

WTF_CSRF_TIME_LIMIT = int(timedelta(days=365).total_seconds())


# Session cookie

SESSION_COOKIE_SAMESITE = "Lax"

SESSION_COOKIE_SECURE = True

SESSION_COOKIE_HTTPONLY = False


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
            "schedule": crontab(minute="15", hour="*"),
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

TALISMAN_ENABLED = False

TALISMAN_CONFIG = {
    "force_https": False,
    "force_https_permanent": False,
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


# Alerts/Reports


def get_slack_api_token() -> str:
    return os.environ.get("SLACK_API_TOKEN", "")


SLACK_API_TOKEN = get_slack_api_token()

WEBDRIVER_BASEURL = "http://superset:8088/"


def get_baseurl_user_friendly() -> str:
    if (ingress := os.environ.get("INGRESS_HOST")) is None:
        return "http://localhost:8088/"
    return f"https://{ingress}/"


WEBDRIVER_BASEURL_USER_FRIENDLY = get_baseurl_user_friendly()

THUMBNAIL_SELENIUM_USER = "admin"

ALERT_REPORTS_EXECUTE_AS = [ExecutorType.SELENIUM]

ALERT_REPORTS_NOTIFICATION_DRY_RUN = False


# Mapbox

MAPBOX_API_KEY = os.environ.get("MAPBOX_API_KEY")
