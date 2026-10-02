"""Validation of incoming request payloads.

Validators take already-parsed data and either return cleaned values or raise
RequestValidationError. They do no I/O, so they are easy to test in isolation.
"""
from .exceptions import RequestValidationError

MAX_DESCRIPTION_LENGTH = 500


def validate_create_todo(data):
    """Return the cleaned description from a create-TODO payload."""
    if not isinstance(data, dict):
        raise RequestValidationError({"body": "Request body must be a JSON object."})

    description = data.get("description")
    if description is None:
        raise RequestValidationError({"description": "This field is required."})
    if not isinstance(description, str):
        raise RequestValidationError({"description": "This field must be a string."})

    description = description.strip()
    if not description:
        raise RequestValidationError({"description": "This field may not be blank."})
    if len(description) > MAX_DESCRIPTION_LENGTH:
        raise RequestValidationError(
            {"description": f"Ensure this field has no more than {MAX_DESCRIPTION_LENGTH} characters."}
        )

    return description
