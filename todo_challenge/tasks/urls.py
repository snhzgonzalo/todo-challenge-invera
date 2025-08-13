from django.urls import path
from .views import TaskListCreateView, TaskDetailView, TaskToggleView

urlpatterns = [
    path("", TaskListCreateView.as_view(), name="task-list-create"),
    path("<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path("<int:pk>/toggle/", TaskToggleView.as_view(), name="task-toggle"),
]
