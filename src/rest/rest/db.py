"""MongoDB connection management.

MongoClient is thread-safe and keeps its own connection pool, so one client
is shared by the whole process. It is created lazily on first use, so that
importing this module needs neither environment variables nor a running
database.
"""
import os
import threading

from django.core.exceptions import ImproperlyConfigured
from pymongo import MongoClient

DATABASE_NAME = "test_db"

# Fail fast with a clear error instead of pymongo's 30s default when Mongo is down.
SERVER_SELECTION_TIMEOUT_MS = 3000

_client = None
_client_lock = threading.Lock()


def _require_env(name):
    value = os.environ.get(name)
    if not value:
        raise ImproperlyConfigured(f"Environment variable {name} is not set.")
    return value


def _build_mongo_uri():
    host = _require_env("MONGO_HOST")
    port = _require_env("MONGO_PORT")
    return f"mongodb://{host}:{port}"


def get_client():
    global _client
    if _client is None:
        with _client_lock:
            # Re-check: another thread may have created it while we waited.
            if _client is None:
                _client = MongoClient(
                    _build_mongo_uri(),
                    serverSelectionTimeoutMS=SERVER_SELECTION_TIMEOUT_MS,
                    tz_aware=True,
                )
    return _client


def get_database():
    return get_client()[DATABASE_NAME]
