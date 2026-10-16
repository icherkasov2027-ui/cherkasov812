import json
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage

from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Project
from .exceptions import NotFoundException, ValidationException, ConflictException

project_post_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['title'],
    properties={
        'title': openapi.Schema(type=openapi.TYPE_STRING, description="Назва проєкту (макс. 200 символів)", max_length=200),
        'description': openapi.Schema(type=openapi.TYPE_STRING, description="Опис проєкту (необов'язково)"),
    }
)

@swagger_auto_schema(
    method='get',
    operation_summary="Отримання списку проєктів",
    operation_description="Повертає фільтрований та відсортований список проєктів із поділом на сторінки.",
    manual_parameters=[
        openapi.Parameter('search', openapi.IN_QUERY, description="Пошук за назвою проєкту", type=openapi.TYPE_STRING),
        openapi.Parameter('sort_by', openapi.IN_QUERY, description="Поле сортування: id, title, created_at, tasks_count", type=openapi.TYPE_STRING, default='id'),
        openapi.Parameter('order', openapi.IN_QUERY, description="Напрям сортування: asc або desc", type=openapi.TYPE_STRING, default='asc'),
        openapi.Parameter('page', openapi.IN_QUERY, description="Номер сторінки", type=openapi.TYPE_INTEGER, default=1),
        openapi.Parameter('page_size', openapi.IN_QUERY, description="Кількість елементів на сторінці (макс. 100)", type=openapi.TYPE_INTEGER, default=20),
    ],
    responses={
        200: "Успішний запит",
        400: "Помилка валідації параметрів",
        404: "Сторінку не знайдено"
    }
)
@swagger_auto_schema(
    method='post',
    operation_summary="Створення нового проєкту",
    operation_description="Створює новий проєкт з перевіркою унікальності назви.",
    request_body=project_post_schema,
    responses={
        201: "Проєкт успішно створено",
        400: "Помилка валідації даних",
        409: "Конфлікт (проєкт із такою назвою вже існує)"
    }
)
@api_view(['GET', 'POST'])
def get_projects(request):
    if request.method == "GET":
        search_query = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sort_by', 'id').strip()
        order = request.GET.get('order', 'asc').strip()

        try:
            page_number = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 20))
        except ValueError:
            raise ValidationException("Параметри 'page' та 'page_size' повинні бути цілими числами.")

        if page_number < 1 or page_size < 1:
            raise ValidationException("Параметри 'page' та 'page_size' повинні бути більше 0.")

        if page_size > 100:
            raise ValidationException("Максимальний розмір сторінки (page_size) — 100.")

        queryset = Project.objects.annotate(tasks_count=Count('tasks'))

        if search_query:
            queryset = queryset.filter(title__icontains=search_query)

        allowed_sort_fields = ['id', 'title', 'created_at', 'tasks_count']
        if sort_by not in allowed_sort_fields:
            raise ValidationException(f"Неможливо сортувати за полем '{sort_by}'. Дозволені: {', '.join(allowed_sort_fields)}.")

        if order not in ['asc', 'desc']:
            raise ValidationException("Параметр 'order' повинен бути 'asc' або 'desc'.")

        order_prefix = '-' if order == 'desc' else ''
        queryset = queryset.order_by(f"{order_prefix}{sort_by}", 'id')

        paginator = Paginator(queryset, page_size)
        try:
            page_obj = paginator.page(page_number)
        except EmptyPage:
            raise NotFoundException(f"Сторінку №{page_number} не знайдено.")

        items = [
            {
                "id": project.id,
                "title": project.title,
                "description": project.description,
                "tasks_count": project.tasks_count,
            }
            for project in page_obj
        ]

        return Response({
            "items": items,
            "total_count": paginator.count,
            "page": page_number,
            "page_size": page_size
        })

    elif request.method == "POST":
        data = request.data if isinstance(request.data, dict) else {}

        title = str(data.get("title", "")).strip()
        description = str(data.get("description", "")).strip()

        if not title:
            raise ValidationException("Поле 'title' є обов'язковим.")

        if len(title) > 200:
            raise ValidationException("Довжина 'title' не може перевищувати 200 символів.")

        if Project.objects.filter(title__iexact=title).exists():
            raise ConflictException(f"Проєкт із назвою '{title}' вже існує.")

        project = Project.objects.create(title=title, description=description)

        return Response({
            "id": project.id,
            "title": project.title,
            "description": project.description
        }, status=status.HTTP_201_CREATED)


@swagger_auto_schema(
    method='post',
    operation_summary="Завантаження обкладинки проєкту",
    operation_description="Приймає файл зображення (JPEG, PNG до 5 МБ) через multipart/form-data.",
    manual_parameters=[
        openapi.Parameter(
            'cover_image',
            openapi.IN_FORM,
            type=openapi.TYPE_FILE,
            description='Зображення обкладинки (JPEG, PNG до 5 МБ)',
            required=True
        )
    ],
    responses={200: 'Успішно', 400: 'Помилка валідації', 404: 'Проєкт не знайдено'}
)
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_project_cover(request, pk):
    try:
        project = Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        return Response({"detail": "Проєкт не знайдено."}, status=status.HTTP_404_NOT_FOUND)

    if 'cover_image' not in request.FILES:
        return Response({"detail": "Файл не передано."}, status=status.HTTP_400_BAD_REQUEST)

    file = request.FILES['cover_image']
    
    if file.size > 5 * 1024 * 1024:
        return Response({"detail": "Розмір файлу перевищує 5 МБ."}, status=status.HTTP_400_BAD_REQUEST)
        
    if not file.name.lower().endswith(('.png', '.jpg', '.jpeg')):
        return Response({"detail": "Дозволені лише формати JPEG та PNG."}, status=status.HTTP_400_BAD_REQUEST)

    if project.cover_image:
        project.cover_image.delete(save=False)

    project.cover_image = file
    project.save()

    cover_url = request.build_absolute_uri(project.cover_image.url)
    return Response({
        "id": project.id, 
        "cover_image_url": cover_url
    }, status=status.HTTP_200_OK)