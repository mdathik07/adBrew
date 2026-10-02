"""Persistence of TODO items in MongoDB.

This is the only module that knows how TODOs are stored. Callers receive
plain dicts and our own exceptions, never pymongo types or errors.
"""
from datetime import datetime, timezone

from pymongo import ASCENDING
from pymongo.errors import ConnectionFailure, PyMongoError

from .db import get_database
from .exceptions import StorageError, StorageUnavailableError

COLLECTION_NAME = "todos"


class TodoRepository:

    def __init__(self, collection):
        self._collection = collection

    def list_todos(self):
        try:
            # list() must stay inside the try: cursors are lazy, so the query
            # only reaches the database when iterated.
            documents = list(
                self._collection.find({}, {"description": 1, "created_at": 1})
                .sort([("created_at", ASCENDING), ("_id", ASCENDING)])
            )
        except PyMongoError as exc:
            raise _translate_error(exc, "list todos") from exc
        return [_to_dict(document) for document in documents]

    def create_todo(self, description):
        document = {"description": description, "created_at": _utc_now()}
        try:
            result = self._collection.insert_one(document)
        except PyMongoError as exc:
            raise _translate_error(exc, "create todo") from exc
        return _to_dict({**document, "_id": result.inserted_id})


def get_todo_repository():
    return TodoRepository(get_database()[COLLECTION_NAME])


def _utc_now():
    # MongoDB stores datetimes with millisecond precision; truncate so the value
    # returned on create matches what a later read returns.
    now = datetime.now(timezone.utc)
    return now.replace(microsecond=now.microsecond // 1000 * 1000)


def _to_dict(document):
    return {
        "id": str(document["_id"]),
        "description": document["description"],
        "created_at": document["created_at"].isoformat(),
    }


def _translate_error(exc, operation):
    if isinstance(exc, ConnectionFailure):
        return StorageUnavailableError(f"Database unavailable while trying to {operation}.")
    return StorageError(f"Database error while trying to {operation}.")
