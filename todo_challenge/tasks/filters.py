import django_filters
from .models import Task

class TaskFilter(django_filters.FilterSet):
    completed = django_filters.BooleanFilter(
        field_name='completed'
    )
    created_at = django_filters.DateFromToRangeFilter(
        field_name='created_at'
    )
    updated_at = django_filters.DateFromToRangeFilter(
        field_name='updated_at'
    )


    class Meta:
        model = Task
        fields = ['completed', 'created_at', 'updated_at']
