from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    UpdateAPIView,
    GenericAPIView
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db import transaction

from .models import Task
from .serializers import TaskSerializer
from .filters import TaskFilter
from .permissions import IsOwner


class TaskBaseView(GenericAPIView):
    """
    Base view para definir queryset de view por usuario
    """
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)


class TaskListCreateView(TaskBaseView, ListCreateAPIView):
    """
    List y Create view unificadas
    GET: Lista todas las tareas del usuario.
    POST: Crea una nueva task
    """
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TaskFilter
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "updated_at", "title"]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TaskDetailView(TaskBaseView, RetrieveUpdateDestroyAPIView):
    """
    Detail view con principio RESTful
    """
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsOwner]


class TaskToggleView(TaskBaseView, UpdateAPIView):
    """
    Actualiza el estado de la tarea especificamente
    """
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        task = self.get_object()
        if "completed" in request.data:
            task.completed = bool(request.data["completed"])
        else:
            task.completed = not task.completed
        task.save(update_fields=["completed"])
        return Response(
            self.get_serializer(task).data,
            status=status.HTTP_200_OK
        )