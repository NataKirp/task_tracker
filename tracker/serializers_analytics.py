from rest_framework import serializers

class BusyEmployeeSerializer(serializers.Serializer):
    """
    Сериализатор для ответа эндпоинта "Занятые сотрудники".
    """
    id = serializers.IntegerField()
    full_name = serializers.SerializerMethodField()
    active_tasks_count = serializers.IntegerField()

    def get_full_name(self, obj):
        """
        Метод, который DRF вызовет для заполнения поля full_name.
        """
        return obj.get_full_name() or obj.username


class ImportantTaskSerializer(serializers.Serializer):
    """
    Сериализатор для ответа эндпоинта "Важные задачи".
    """
    important_task = serializers.CharField(source='name')
    due_date = serializers.DateField()
    assignees = serializers.ListField(child=serializers.CharField())
