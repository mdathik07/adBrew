"""HTTP layer for the TODO API.

Views only translate between HTTP and the application layers. Exceptions
raised here are turned into error responses by rest.exception_handlers.
"""
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from .responses import success_response
from .todo_repository import get_todo_repository
from .validators import validate_create_todo


class TodoListView(APIView):
    parser_classes = [JSONParser]

    def get(self, request):
        todos = get_todo_repository().list_todos()
        return success_response(todos)

    def post(self, request):
        # Validate first: bad input is rejected without touching the database.
        description = validate_create_todo(request.data)
        todo = get_todo_repository().create_todo(description)
        return success_response(todo, status.HTTP_201_CREATED)
