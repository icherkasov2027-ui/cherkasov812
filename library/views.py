from django.http import JsonResponse
from django.db.models import Count, Q
from django.core.paginator import Paginator
from .models import Project

def get_projects(request):
    page_number = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    search = request.GET.get('search', '')
    sort_by = request.GET.get('sort_by', 'id')
    order = request.GET.get('order', 'asc')

    projects_query = Project.objects.all()

    if search:
        projects_query = projects_query.filter(title__icontains=search)

    # Рахуємо кількість задач (tasks) одним SQL-запитом через annotate
    projects_query = projects_query.annotate(tasks_count=Count('tasks'))

    if sort_by == 'title':
        ordering = 'title' if order == 'asc' else '-title'
    else:
        ordering = 'id' if order == 'asc' else '-id'

    projects_query = projects_query.order_by(ordering, 'id')

    # 6. Пагінація
    paginator = Paginator(projects_query, page_size)
    page_obj = paginator.get_page(page_number)

    data = []
    for project in page_obj:
        data.append({
            'id': project.id,
            'title': project.title,
            'description': project.description,
            'tasks_count': project.tasks_count, # Без додаткових запитів до бази
        })

    return JsonResponse({
        'items': data,
        'total_count': paginator.count,
        'page': page_number,
        'page_size': page_size
    }, json_dumps_params={'ensure_ascii': False})