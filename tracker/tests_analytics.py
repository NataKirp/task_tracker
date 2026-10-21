from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User

from .models import Task


class AnalyticsAPITests(APITestCase):
    """
    Тесты для эндпоинтов аналитики.
    """

    def setUp(self):
        # Создаем 3 сотрудников
        self.user1 = User.objects.create_user(
            username="user1", first_name="Иван", last_name="Первый"
        )
        self.user2 = User.objects.create_user(
            username="user2", first_name="Анна", last_name="Вторая"
        )
        self.user3 = User.objects.create_user(
            username="user3", first_name="Петр", last_name="Третий"
        )

        # user1 - 2 активные задачи (самый загруженный)
        Task.objects.create(
            name="Задача 1",
            assignee=self.user1,
            status="in_progress",
            due_date=timezone.now().date(),
        )
        Task.objects.create(
            name="Задача 2",
            assignee=self.user1,
            status="in_progress",
            due_date=timezone.now().date(),
        )

        # user2 - 1 активная задача
        Task.objects.create(
            name="Задача 3",
            assignee=self.user2,
            status="in_progress",
            due_date=timezone.now().date(),
        )

        # user3 - 0 задач (наименее загруженный)

        self.client.force_authenticate(user=self.user1)
        self.client.force_authenticate(user=self.user2)
        self.client.force_authenticate(user=self.user3)
        self.busy_url = reverse("analytics-busy-employees")
        self.important_url = reverse("analytics-important-tasks")

    def test_busy_employees(self):
        """Проверяем сортировку сотрудников по нагрузке."""
        response = self.client.get(self.busy_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Ожидаем 3 сотрудников
        self.assertEqual(len(response.data), 3)

        # Проверяем сортировку: user1 (2 задачи) -> user2 (1 задача) -> user3 (0 задач)
        self.assertEqual(response.data[0]["id"], self.user1.id)
        self.assertEqual(response.data[0]["active_tasks_count"], 2)
        self.assertEqual(response.data[1]["id"], self.user2.id)
        self.assertEqual(response.data[2]["id"], self.user3.id)

    def test_important_tasks_logic(self):
        """Проверяем поиск важных задач (родитель 'new', подзадача 'in_progress')."""
        # Создаем "важную задачу" и её дочернюю
        important_task = Task.objects.create(
            name="Важная задача",
            assignee=self.user1,
            status="new",
            due_date=timezone.now().date(),
        )
        Task.objects.create(
            name="Подзадача в работе",
            parent_task=important_task,
            assignee=self.user1,
            status="in_progress",
            due_date=timezone.now().date(),
        )

        response = self.client.get(self.important_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Ожидаем, что вернется ровно 1 важная задача
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["important_task"], "Важная задача")

        # Проверяем, что в списке assignees есть наименее загруженный (user3)
        # Ведь user3 = 0 задач, а user1 = 2 задачи.
        self.assertIn("Петр Третий", response.data[0]["assignees"])
