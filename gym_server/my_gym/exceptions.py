from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def core_exception_handler(exc, context):
    response = exception_handler(exc, context)
    handlers = {
        'ValidationError': _handle_generic_error,
        'ValueError': _handle_generic_error,
        'TypeError': _handle_generic_error,
        'PermissionError': _handle_generic_error
    }
    exception_class = exc.__class__.__name__

    if exception_class in handlers:
        return handlers[exception_class](exc, context, response)

    return response


def _handle_generic_error(exc, context, response):
    try:
        response.data = {
            'errors': response.data
        }
        return response
    except AttributeError:
        data = {
            'errors': f'{exc}'
        }
        return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
