from django_tables2 import RequestConfig

from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.http import HttpResponseBase

from .forms import (
    LoginForm,
    RegisterForm,
    TaskForm,
    TaskUpdateForm,
    TaskFilterForm
)
from .mixins import ApiSessionMixin, SessionRequiredMixin
from .tables import TaskTable


class RedirectToLoginView(View):
    """Redirige / a login o tareas según sesión."""
    def get(self, request):
        if request.session.get("access"):
            return redirect("web:tasks")
        return redirect("web:login")


class LoginView(ApiSessionMixin, View):
    def get(self, request):
        response = None
        if request.session.get("access"):
            response = redirect("web:tasks")
        else:
            response = render(request, "web/login.html", {"form": LoginForm()})
        return response

    def post(self, request):
        context = {"form": LoginForm(request.POST), "show_register": True}
        if request.session.get("access"):
            result = redirect("web:tasks")
        elif not context["form"].is_valid():
            result = render(request, "web/login.html", context)
        else:
            res = self.api_request(
                "POST",
                "/users/auth/token/",
                request,
                data=context["form"].cleaned_data,
                token_required=False,
                error_msg="Usuario o contraseña incorrectos."
            )
            if res and res.status_code == 200:
                tokens = res.json()
                request.session["access"] = tokens.get("access")
                request.session["refresh"] = tokens.get("refresh")
                messages.success(request, "Inicio de sesión exitoso.")
                result = redirect("web:tasks")
            else:
                result = render(request, "web/login.html", context)
        return result


class RegisterView(ApiSessionMixin, View):
    def get(self, request):
        return render(request, "web/register.html", {"form": RegisterForm()})

    def post(self, request):
        context = {"form": RegisterForm(request.POST)}
        if not context["form"].is_valid():
            result = render(request, "web/register.html", context)
        else:
            res = self.api_request(
                "POST",
                "/users/auth/register/",
                request,
                data=context["form"].cleaned_data,
                token_required=False,
                error_msg="Error al registrar usuario."
            )
            if res and res.status_code == 201:
                messages.success(request, "Usuario registrado. Ahora puede iniciar sesión.")
                result = redirect("web:login")
            else:
                result = render(request, "web/register.html", context)
        return result


class LogoutView(
    SessionRequiredMixin,
    View
):
    def get(self, request):
        request.session.flush()
        messages.info(request, "Sesión cerrada.")
        return redirect("web:login")


class TaskListCreateView(
    SessionRequiredMixin,
    ApiSessionMixin, 
    View
):
    def get(self, request):
        filter_form = TaskFilterForm(request.GET or None)
        params = {}
        if filter_form.is_valid():
            data = filter_form.cleaned_data
            if data.get("completed"):
                params["completed"] = data["completed"]
            if data.get("created_at_after"):
                params["created_at_after"] = data["created_at_after"].isoformat()
            if data.get("created_at_before"):
                params["created_at_before"] = data["created_at_before"].isoformat()
            if data.get("updated_at_after"):
                params["updated_at_after"] = data["updated_at_after"].isoformat()
            if data.get("updated_at_before"):
                params["updated_at_before"] = data["updated_at_before"].isoformat()

        resp = self.api_request(
            "GET", "/", request,
            error_msg="No se pudieron obtener las tareas.",
            params=params or None,
        )
        if isinstance(resp, HttpResponseBase):
            return resp

        tasks = []
        if resp and resp.status_code == 200:
            try:
                data = resp.json()
            except ValueError:
                data = []
            tasks = data.get("results", data) if isinstance(data, dict) else data

        table = TaskTable(tasks)
        RequestConfig(request, paginate={"per_page": 10}).configure(table)

        return render(request, "web/tasks.html", {
            "form": TaskForm(),
            "filter_form": filter_form,
            "table": table,
        })

    def post(self, request):
        form = TaskForm(request.POST)
        if not form.is_valid():
            return redirect("web:tasks")

        resp = self.api_request(
            "POST", "/", request,
            data=form.cleaned_data,
            success_msg="Tarea creada con éxito.",
            error_msg="Error al crear tarea.",
        )
        if isinstance(resp, HttpResponseBase):
            return resp
        return redirect("web:tasks")


class TaskDetailPageView(
    SessionRequiredMixin,
    ApiSessionMixin,
    View
):
    def get(self, request, pk):
        resp = self.api_request(
            "GET", f"/{pk}/", request,
            error_msg="No se pudo cargar la tarea."
        )
        if isinstance(resp, HttpResponseBase):
            return resp
        if not resp or resp.status_code != 200:
            messages.error(request, "Tarea no encontrada")
            return redirect("web:tasks")
        try:
            task = resp.json()
        except ValueError:
            messages.error(request, "Respuesta inválida del servidor.")
            return redirect("web:tasks")

        return render(request, "web/tasks_detail.html", {"task": task})


class TaskUpdateView(
    SessionRequiredMixin,
    ApiSessionMixin,
    View
):
    def get(self, request, pk):
        resp = self.api_request(
            "GET", f"/{pk}/", request,
            error_msg="No se pudo cargar la tarea."
        )
        if isinstance(resp, HttpResponseBase):
            return resp
        if not resp or resp.status_code != 200:
            messages.error(request, "Tarea no encontrada")
            return redirect("web:tasks")

        try:
            data = resp.json()
        except ValueError:
            messages.error(request, "Respuesta inválida del servidor.")
            return redirect("web:tasks")

        form = TaskUpdateForm(initial={
            "title": data.get("title", ""),
            "description": data.get("description", ""),
            "completed": bool(data.get("completed")),
        })
        return render(request, "web/tasks_edit.html", {"form": form, "task_id": pk})

    def post(self, request, pk):
        form = TaskUpdateForm(request.POST)
        if not form.is_valid():
            return render(request, "web/tasks_edit.html", {"form": form, "task_id": pk})

        payload = {
            "title": form.cleaned_data["title"],
            "description": form.cleaned_data.get("description", ""),
            "completed": bool(form.cleaned_data.get("completed")),
        }

        resp = self.api_request(
            "PATCH", f"/{pk}/", request,
            data=payload,
            success_msg="Tarea actualizada.",
            error_msg="No se pudo actualizar la tarea."
        )
        if isinstance(resp, HttpResponseBase):
            return resp
        if resp and 200 <= resp.status_code < 300:
            return redirect("web:task-detail", pk=pk)
        try:
            errors = resp.json()
        except Exception:
            errors = {}
        for field, msgs in (errors.items() if isinstance(errors, dict) else []):
            if field in form.fields:
                form.add_error(field, "; ".join(msgs if isinstance(msgs, list) else [str(msgs)]))
        return render(request, "web/tasks_edit.html", {"form": form, "task_id": pk})


class TaskToggleView(SessionRequiredMixin, ApiSessionMixin, View):
    def post(self, request, pk):
        resp = self.api_request(
            "PATCH",
            f"/{pk}/toggle/",
            request,
            error_msg="No se pudo actualizar la tarea."
        )
        if isinstance(resp, HttpResponseBase):
            return resp

        if resp and resp.status_code == 200:
            try:
                data = resp.json()
                messages.success(
                    request,
                    "Tarea marcada como completada." if data.get("completed") else "Tarea reabierta."
                )
            except ValueError:
                messages.error(request, "Error al procesar la respuesta del servidor.")
        return redirect(next_url or "web:tasks")


class TaskDeleteView(
    SessionRequiredMixin,
    ApiSessionMixin,
    View
):
    def post(self, request, pk):
        resp = self.api_request(
            "DELETE",
            f"/{pk}/",
            request,
            success_msg="Tarea eliminada.",
            error_msg="No se pudo eliminar la tarea."
        )
        if isinstance(resp, HttpResponseBase):
            return resp
        return redirect("web:tasks")