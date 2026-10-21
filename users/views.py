from rest_framework import viewsets

from .models import Position, User
from .serializers import PositionSerializer, UserSerializer


class PositionViewSet(viewsets.ModelViewSet):
    """
    API эндпоинт для работы с должностями.
    """

    queryset = Position.objects.all()
    serializer_class = PositionSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API эндпоинт для работы с сотрудниками.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
