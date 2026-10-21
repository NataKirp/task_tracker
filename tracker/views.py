from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Task
from .serializers import TaskSerializer
from .serializers_analytics import (BusyEmployeeSerializer,
                                    ImportantTaskSerializer)

User = get_user_model()


class TaskViewSet(viewsets.ModelViewSet):
    """
    API эндпоинт для работы с задачами (CRUD).
    """

    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class AnalyticsViewSet(viewsets.ViewSet):
    """
    Кастомные эндпоинты для аналитики по задачам и сотрудникам.
    """

    @extend_schema(responses=BusyEmployeeSerializer(many=True))
    @action(detail=False, methods=["get"])
    def busy_employees(self, request):
        """
        Список сотрудников, отсортированный по количеству активных задач (по убыванию).
        """
        employees = User.objects.annotate(
            active_tasks_count=Count("tasks", filter=Q(tasks__status="in_progress"))
        ).order_by("-active_tasks_count")

        # Передаем QuerySet (объекты User) напрямую в сериализатор!
        serializer = BusyEmployeeSerializer(employees, many=True)
        return Response(serializer.data)

    @extend_schema(responses=ImportantTaskSerializer(many=True))
    @action(detail=False, methods=["get"])
    def important_tasks(self, request):
        """
        Задачи, которые не взяты в работу, но от которых зависят другие задачи, взятые в работу.
        С подбором исполнителей.
        """
        # Находим "Важные задачи" (Статус 'new', но есть подзадачи в статусе 'in_progress')
        important_tasks = Task.objects.filter(
            status="new", subtasks__status="in_progress"
        ).distinct()

        if not important_tasks.exists():
            return Response([])

        # Считаем загруженность всех сотрудников
        # Получаем список сотрудников и количество их активных задач
        users_with_load = User.objects.annotate(
            active_load=Count("tasks", filter=Q(tasks__status="in_progress"))
        )

        # Находим минимальную загруженность
        min_load = users_with_load.order_by("active_load").first().active_load

        result = []
        for task in important_tasks:
            # Подбираем кандидатов для каждой важной задачи
            candidates = []

            # Наименее загруженные сотрудники (их может быть несколько)
            least_busy = users_with_load.filter(active_load=min_load)
            candidates.extend(least_busy)

            # Проверяем исполнителя самой важной (родительской) задачи
            if task.assignee:
                # Считаем его текущую загрузку
                assignee_load = task.assignee.tasks.filter(status="in_progress").count()
                # Если у него не перегруз (максимум на 2 задачи больше, чем у наименее загруженного)
                if assignee_load <= min_load + 2:
                    # Добавляем его в список кандидатов, если его там еще нет
                    if task.assignee not in candidates:
                        candidates.append(task.assignee)

            # Формируем ответ
            result.append(
                {
                    "name": task.name,
                    "due_date": task.due_date,
                    "assignees": [
                        user.get_full_name() or user.username for user in candidates
                    ],
                }
            )

        serializer = ImportantTaskSerializer(result, many=True)
        return Response(serializer.data)
