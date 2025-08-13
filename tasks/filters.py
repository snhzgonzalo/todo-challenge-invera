from django_filters import (
    FilterSet,
    BooleanFilter,
    DateFromToRangeFilter
)

from .models import Task


class TaskFilter(FilterSet):
    """
    Filtros para API.
    """
    completed = BooleanFilter(
        field_name='completed'
    )
    created_at = DateFromToRangeFilter(
        field_name='created_at'
    )
    updated_at = DateFromToRangeFilter(
        field_name='updated_at'
    )

    class Meta:
        model = Task
        fields = ['completed', 'created_at', 'updated_at']
