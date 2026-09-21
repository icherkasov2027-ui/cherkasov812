from django.http import JsonResponse
from django.db.models import Count, Q
from django.core.paginator import Paginator
from .models import Author

def get_authors(request):
    page_number = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    search = request.GET.get('search', '')
    sort_by = request.GET.get('sort_by', 'id')
    order = request.GET.get('order', 'asc')

    authors_query = Author.objects.all()

    if search:
        authors_query = authors_query.filter(
            Q(first_name__icontains=search) | Q(last_name__icontains=search)
        )

    authors_query = authors_query.annotate(books_count=Count('books'))

    if sort_by == 'name':
        ordering = 'first_name' if order == 'asc' else '-first_name'
    else:
        ordering = 'id' if order == 'asc' else '-id'

    authors_query = authors_query.order_by(ordering, 'id')

    paginator = Paginator(authors_query, page_size)
    page_obj = paginator.get_page(page_number)

    data = []
    for author in page_obj:
        data.append({
            'id': author.id,
            'first_name': author.first_name,
            'last_name': author.last_name,
            'email': author.email,
            'books_count': author.books_count, # Без доп. запросов к базе
        })

    return JsonResponse({
        'items': data,
        'total_count': paginator.count,
        'page': page_number,
        'page_size': page_size
    }, json_dumps_params={'ensure_ascii': False})