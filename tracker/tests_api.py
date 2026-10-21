from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User, Position
from .models import Task
from datetime import timedelta
from django.utils import timezone


class TaskAPITests(APITestCase):
    """
    Тесты для эндпоинтов задач (/api/tasks/).
    """

    def setUp(self):
        # Создаем пользователя для связи
        self.user = User.objects.create_user(username="testuser", password="pass")

        # Создаем тестовую задачу
        self.task = Task.objects.create(
            name="Тестовая задача",
            status="in_progress",
            assignee=self.user,
            due_date=timezone.now().date() + timedelta(days=5)
        )

        # reverse() автоматически строит URL по имени маршрута,
        # заданному в роутере (basename='task-list' или 'task-detail')
        self.list_url = reverse('task-list')
        self.detail_url = reverse('task-detail', kwargs={'pk': self.task.pk})

    def test_list_tasks(self):
        """GET /api/tasks/ — проверяем, что возвращается список задач (200 OK)."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем, что в списке ровно 1 задача
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Тестовая задача")

    def test_create_task(self):
        """POST /api/tasks/ — проверяем создание новой задачи (201 Created)."""
        data = {
            'name': 'Новая задача из API',
            'status': 'new',
            'due_date': str(timezone.now().date() + timedelta(days=10)),  # Дату передаем строкой
            'assignee_id': self.user.id
        }
        response = self.client.post(self.list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)
        self.assertEqual(response.data['name'], 'Новая задача из API')
        # Проверяем, что вложенный сериализатор вернул данные пользователя
        self.assertEqual(response.data['assignee']['id'], self.user.id)

    def test_update_task(self):
        """PATCH /api/tasks/{id}/ — проверяем частичное обновление (200 OK)."""
        data = {'status': 'done'}
        response = self.client.patch(self.detail_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем в базе данных, что статус реально изменился
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'done')
