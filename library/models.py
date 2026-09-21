from django.db import models

class Author(models.Model):
    first_name = models.CharField(max_length=100, null=False)
    last_name = models.CharField(max_length=100, null=False)
    email = models.EmailField(unique=True) 

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Book(models.Model):
    title = models.CharField(max_length=200, null=False)
    description = models.TextField(max_length=4000, blank=True, null=True)
    published_date = models.DateField(null=False)
    page_count = models.IntegerField(null=False)
    
    author = models.ForeignKey(Author, on_delete=models.RESTRICT, related_name='books')
    
    created_at = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)

    def __str__(self):
        return self.title