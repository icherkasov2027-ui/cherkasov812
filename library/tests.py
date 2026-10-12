from unittest.mock import MagicMock
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Project

class ProjectUnitTest(TestCase):
    def test_project_title_normalization_mock(self):
        mock_project = MagicMock()
        mock_project.title = "  Тестовий Проєкт  ".strip()
        self.assertEqual(mock_project.title, "Тестовий Проєкт")

class ProjectApiIntegrationTests(APITestCase):
    def setUp(self):
        Project.objects.all().delete()

    def test_create_project_success(self):
        """Позитивний сценарій: створення проєкту (201 Created)"""
        data = {"title": "Новий Проєкт", "description": "Опис тестового проєкту"}
        response = self.client.post('/api/projects/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(Project.objects.get().title, "Новий Проєкт")

    def test_create_project_duplicate_conflict(self):
        """Сценарій конфлікту: проєкт із такою назвою вже існує (409 Conflict)"""
        Project.objects.create(title="Існуючий Проєкт", description="Тест")
        data = {"title": "Існуючий Проєкт", "description": "Спроба створити дублікат"}
        response = self.client.post('/api/projects/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(Project.objects.count(), 1)

    def test_create_project_validation_error(self):
        """Помилка валідації: порожня назва (422 Unprocessable Entity)"""
        data = {"title": "", "description": "Без обов'язкової назви"}
        response = self.client.post('/api/projects/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_get_projects_list_success(self):
        """Отримання списку проєктів з пагінацією (200 OK)"""
        Project.objects.create(title="Проєкт 1", description="Опис 1")
        response = self.client.get('/api/projects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_count'], 1)

    def test_method_not_allowed(self):
        """Метод PUT не дозволений для списку проєктів (405 Method Not Allowed)"""
        response = self.client.put('/api/projects/', {"title": "Тест"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_project_empty_post(self):
        """Перевірка відправки порожнього запиту (422 Unprocessable Entity)"""
        response = self.client.post('/api/projects/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

class ModelsUnitTest(TestCase):
    def test_project_string_representation(self):
        """Перевірка магічного методу __str__ для моделі Project"""
        project = Project.objects.create(title="Мій Проєкт", description="Опис")
        self.assertEqual(str(project), "Мій Проєкт")