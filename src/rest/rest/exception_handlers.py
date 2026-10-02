"""Maps exceptions raised in API views to error responses.

Registered via REST_FRAMEWORK["EXCEPTION_HANDLER"], so views never need
try/except for these cases. Every error leaves the API in the same envelope.
"""
import logging

from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import exceptions as drf_exceptions
from rest_framework import status

from .exceptions import RequestValidationError, StorageError, StorageUnavailableError
from .responses import error_response

logger = logging.getLogger(__name__)


def api_exception_handler(exc, context):
    # Same conversions DRF's default handler applies to Django's exceptions.
    if isinstance(exc, Http404):
        exc = drf_exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = drf_exceptions.PermissionDenied()

    if isinstance(exc, RequestValidationError):
        return error_response(
            "validation_error", str(exc), status.HTTP_400_BAD_REQUEST, details=exc.errors
        )

    # Subclass first: StorageUnavailableError is also a StorageError.
    if isinstance(exc, StorageUnavailableError):
        logger.warning("%s (%s)", exc, _view_name(context), exc_info=exc)
        return error_response(
            "database_unavailable",
            "The database is temporarily unavailable. Please try again later.",
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    if isinstance(exc, StorageError):
        logger.error("%s (%s)", exc, _view_name(context), exc_info=exc)
        return error_response(
            "database_error", "A database error occurred.", status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    if isinstance(exc, drf_exceptions.APIException):
        return error_response(exc.default_code, _api_exception_message(exc), exc.status_code)

    logger.error("Unhandled exception in %s", _view_name(context), exc_info=exc)
    return error_response(
        "internal_error", "An unexpected error occurred.", status.HTTP_500_INTERNAL_SERVER_ERROR
    )


def _api_exception_message(exc):
    # ParseError, MethodNotAllowed etc. carry a plain-string detail; anything
    # structured falls back to the exception's generic default message.
    if isinstance(exc.detail, str):
        return str(exc.detail)
    return str(exc.default_detail)


def _view_name(context):
    view = context.get("view")
    return type(view).__name__ if view is not None else "unknown view"
