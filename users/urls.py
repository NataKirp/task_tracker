from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PositionViewSet, UserViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"positions", PositionViewSet, basename="position")

urlpatterns = [
    path("", include(router.urls)),
]
