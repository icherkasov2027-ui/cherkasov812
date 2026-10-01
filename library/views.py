import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage

from .models import Project
from .exceptions import NotFoundException, ValidationException, ConflictException


@require_http_methods(["GET", "POST"])
def get_projects(request):
    if request.method == "GET":
        # 1. Отримуємо та валідуємо параметри запиту (Крок 1 і 4 методички)
        search_query = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sort_by', 'id').strip()
        order = request.GET.get('order', 'asc').strip()

        # Валідація числових параметрів пагінації
        try:
            page_number = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 20))
        except ValueError:
            raise ValidationException("Параметри 'page' та 'page_size' повинні бути цілими числами.")

        if page_number < 1 or page_size < 1:
            raise ValidationException("Параметри 'page' та 'page_size' повинні бути більше 0.")

        if page_size > 100:
            raise ValidationException("Максимальний розмір сторінки (page_size) — 100.")

        # 2. Оптимізований запит з анотацією (N+1)
        queryset = Project.objects.annotate(tasks_count=Count('tasks'))

        # 3. Фільтрація
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)

        # 4. Сортування
        allowed_sort_fields = ['id', 'title', 'created_at', 'tasks_count']
        if sort_by not in allowed_sort_fields:
            raise ValidationException(f"Неможливо сортувати за полем '{sort_by}'. Дозволені: {', '.join(allowed_sort_fields)}.")

        if order not in ['asc', 'desc']:
            raise ValidationException("Параметр 'order' повинен бути 'asc' або 'desc'.")

        order_prefix = '-' if order == 'desc' else ''
        queryset = queryset.order_by(f"{order_prefix}{sort_by}", 'id')

        # 5. Пагінація
        paginator = Paginator(queryset, page_size)
        try:
            page_obj = paginator.page(page_number)
        except EmptyPage:
            raise NotFoundException(f"Сторінку №{page_number} не знайдено.")

        # 6. Формування результату
        items = [
            {
                "id": project.id,
                "title": project.title,
                "description": project.description,
                "tasks_count": project.tasks_count,
            }
            for project in page_obj
        ]

        return JsonResponse({
            "items": items,
            "total_count": paginator.count,
            "page": page_number,
            "page_size": page_size
        })

    elif request.method == "POST":
        # Створення нового проєкту з валідацією DTO
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            raise ValidationException("Некоректний формат JSON у тілі запиту.")

        title = data.get("title", "").strip()
        description = data.get("description", "").strip()

        if not title:
            raise ValidationException("Поле 'title' є обов'язковим.")

        if len(title) > 200:
            raise ValidationException("Довжина 'title' не може перевищувати 200 символів.")

        # Перевірка бізнес-правила (унікальність назви)
        if Project.objects.filter(title__iexact=title).exists():
            raise ConflictException(f"Проєкт із назвою '{title}' вже існує.")

        project = Project.objects.create(title=title, description=description)

        return JsonResponse({
            "id": project.id,
            "title": project.title,
            "description": project.description
        }, status=201)