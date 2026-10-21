from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "status", "assignee", "due_date", "parent_task")
    list_filter = ("status", "assignee", "due_date")
    search_fields = ("name", "assignee__username", "assignee__first_name")
