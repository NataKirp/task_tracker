from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, AnalyticsViewSet

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'analytics', AnalyticsViewSet, basename='analytics')

urlpatterns = [
    path('', include(router.urls)),
]
