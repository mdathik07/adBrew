"""Application-level exceptions.

Lower layers raise these instead of library-specific errors, so callers
never need to import pymongo to handle a storage failure.
"""


class RequestValidationError(Exception):
    """The request body failed validation.

    `errors` maps each offending field to a human-readable message.
    """

    def __init__(self, errors):
        super().__init__("Invalid request body.")
        self.errors = errors


class StorageError(Exception):
    """The persistence layer failed to complete an operation."""


class StorageUnavailableError(StorageError):
    """The database could not be reached (down, unreachable or timed out)."""
