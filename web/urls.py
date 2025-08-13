from django.urls import path

from .views import (
    RedirectToLoginView,
    LoginView,
    RegisterView,
    LogoutView,
    TaskListCreateView,
    TaskDetailPageView,
    TaskUpdateView,
    TaskToggleView,
    TaskDeleteView
)

app_name = "web"

urlpatterns = [
    path("", RedirectToLoginView.as_view(), name="root"),
    path("login/", LoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("tasks/", TaskListCreateView.as_view(), name="tasks"),
    path("tasks/<int:pk>/", TaskDetailPageView.as_view(), name="task-detail"),
    path("tasks/<int:pk>/edit/", TaskUpdateView.as_view(), name="task-edit"),
    path("tasks/<int:pk>/toggle/", TaskToggleView.as_view(), name="task-toggle"),
    path("tasks/<int:pk>/delete/", TaskDeleteView.as_view(), name="task-delete"),
]
