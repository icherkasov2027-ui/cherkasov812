from django.http import JsonResponse
from .exceptions import ValidationException, NotFoundException, ConflictException, DomainException

class ExceptionHandlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Перехоплюємо всі помилки прямо під час обробки запиту
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            return self.process_exception(request, e)

    def process_exception(self, request, exception):
        if isinstance(exception, ValidationException):
            return JsonResponse({
                "type": "about:blank",
                "title": "Business rule violation",
                "status": 422,
                "detail": str(exception)
            }, status=422)
        elif isinstance(exception, NotFoundException):
            return JsonResponse({
                "type": "about:blank",
                "title": "Resource not found",
                "status": 404,
                "detail": str(exception)
            }, status=404)
        elif isinstance(exception, ConflictException):
            return JsonResponse({
                "type": "about:blank",
                "title": "Conflict",
                "status": 409,
                "detail": str(exception)
            }, status=409)
        elif isinstance(exception, DomainException):
            return JsonResponse({
                "type": "about:blank",
                "title": "Bad Request",
                "status": 400,
                "detail": str(exception)
            }, status=400)
        
        # Для всіх інших невідомих помилок (500)
        return JsonResponse({
            "type": "about:blank",
            "title": "Internal Server Error",
            "status": 500,
            "detail": "Внутрішня помилка сервера."
        }, status=500)