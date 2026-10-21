from rest_framework import viewsets
from .models import Task
from .serializers import TaskSerializer

class TaskViewSet(viewsets.ModelViewSet):
    """
    API эндпоинт для работы с задачами.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
