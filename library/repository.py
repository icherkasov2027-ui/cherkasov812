from .models import Author, Book

class BookRepository:
    @staticmethod
    def get_all():
        return Book.objects.select_related('author').all()

    @staticmethod
    def get_by_id(book_id):
        return Book.objects.select_related('author').filter(id=book_id).first()

    @staticmethod
    def create(data: dict):
        return Book.objects.create(**data)

    @staticmethod
    def update(book_id, data: dict):
        book = Book.objects.filter(id=book_id).first()
        if not book:
            return False
        for key, value in data.items():
            setattr(book, key, value)
        book.save()
        return True

    @staticmethod
    def delete(book_id):
        count, _ = Book.objects.filter(id=book_id).delete()
        return count > 0