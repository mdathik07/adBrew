"""Builders for the API's response envelope.

Every response body has exactly one top-level key:
    success: {"data": ...}
    failure: {"error": {"code": ..., "message": ..., "details": ...}}
"""
from rest_framework import status
from rest_framework.response import Response


def success_response(data, status_code=status.HTTP_200_OK):
    return Response({"data": data}, status=status_code)


def error_response(code, message, status_code, details=None):
    error = {"code": code, "message": message}
    if details is not None:
        error["details"] = details
    return Response({"error": error}, status=status_code)
