import uuid
import os
from django.db import models

def project_cover_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('uploads/covers/', filename)


class Project(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название проекта")
    description = models.TextField(blank=True, verbose_name="Описание проекта")
    created_at = models.DateTimeField(auto_now_add=True)
    
    cover_image = models.ImageField(upload_to=project_cover_path, null=True, blank=True, verbose_name="Обложка проекта")

    def __str__(self):
        return self.title


class Task(models.Model):
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    title = models.CharField(max_length=255, verbose_name="Название задачи")
    description = models.TextField(blank=True, verbose_name="Описание задачи")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateField(null=True, blank=True, verbose_name="Крайний срок (Дедлайн)")
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    text = models.TextField(verbose_name="Текст комментария")
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Комментарий к {self.task.title}"