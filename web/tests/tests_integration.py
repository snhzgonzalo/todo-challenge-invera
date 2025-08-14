import json
import pytest
import requests
from django.test import TestCase
from django.urls import reverse
from django.http import HttpResponse
from unittest.mock import patch

pytestmark = pytest.mark.django_db

class TestTasksViewsIntegration(TestCase):
    def iniciar_sesion(self, access="A", refresh="R"):
        session = self.client.session
        session["access"] = access
        session["refresh"] = refresh
        session.save()

    def api_response(self, status=200, data=None):
        response = requests.Response()
        response.status_code = status
        response.headers["Content-Type"] = "application/json"
        response._content = b"" if data is None else json.dumps(data).encode()
        return response

    def test_tasks_get_requiere_sesion_redirige_login(self):
        response = self.client.get(reverse("web:tasks"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("web:login"))

    def test_tasks_get_ok_lista(self):
        self.iniciar_sesion()
        with patch("web.mixins.requests.request", return_value=self.api_response(200, {"results": []})):
            response = self.client.get(reverse("web:tasks"))
        self.assertEqual(response.status_code, 200)

    def test_tasks_post_crea_y_redirige(self):
        self.iniciar_sesion()
        with patch("web.mixins.requests.request", return_value=self.api_response(201, {"id": 1})):
            response = self.client.post(reverse("web:tasks"), {"title": "t", "description": ""})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("web:tasks"))

    def test_task_detail_404_redirige_tasks(self):
        self.iniciar_sesion()
        with patch("web.mixins.requests.request", return_value=self.api_response(404, {"detail": "nf"})):
            response = self.client.get(reverse("web:task-detail", args=[999]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("web:tasks"))

    def test_task_detail_200_renderiza(self):
        self.iniciar_sesion()
        with patch("web.mixins.requests.request", return_value=self.api_response(200, {"id": 1, "title": "t"})):
            response = self.client.get(reverse("web:task-detail", args=[1]))
        self.assertEqual(response.status_code, 200)

    def test_task_edit_get_200(self):
        self.iniciar_sesion()
        with patch("web.mixins.requests.request", return_value=self.api_response(200, {"id": 1, "title": "t", "description": "", "completed": False})):
            response = self.client.get(reverse("web:task-edit", args=[1]))
        self.assertEqual(response.status_code, 200)

    def test_task_edit_post_ok_redirige_detalle(self):
        self.iniciar_sesion()
        with patch("web.mixins.requests.request", return_value=self.api_response(200, {"id": 1})):
            response = self.client.post(reverse("web:task-edit", args=[1]), {"title": "t", "description": "", "completed": True})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("web:task-detail", args=[1]))

    def test_task_toggle_post_ok_respeta_next(self):
        self.iniciar_sesion()
        with patch("web.mixins.requests.request", return_value=self.api_response(200, {"completed": True})):
            next_url = reverse("web:task-detail", args=[1])
            response = self.client.post(reverse("web:task-toggle", args=[1]), {"next": next_url})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, next_url)

    def test_task_delete_post_redirige_tasks(self):
        self.iniciar_sesion()
        with patch("web.mixins.requests.request", return_value=self.api_response(204, {})):
            response = self.client.post(reverse("web:task-delete", args=[1]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("web:tasks"))
