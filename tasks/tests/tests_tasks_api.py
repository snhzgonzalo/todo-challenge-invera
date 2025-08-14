from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.factories import UserFactory
from ..models import Task
from ..factories import TaskFactory

User = get_user_model()


class TestTasksAPI(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other = UserFactory()
        self.client.force_authenticate(user=self.user)

        batch_pending = TaskFactory.create_batch(2, user=self.user, completed=False)
        batch_done = TaskFactory.create_batch(2, user=self.user, completed=True)

        self.tarea1 = batch_pending[0]
        self.tarea2 = batch_done[0]
        self.tarea3 = batch_pending[1]
        self.tarea4 = batch_done[1]
        self.tarea5 = TaskFactory(
            user=self.user,
            title="Buscar keyword unica",
            description="Busqueda",
            completed=False,
        )

        self.other_task = TaskFactory(
            user=self.other, title="Ajena", description="Tarea ajena", completed=False
        )

        self.list_url = reverse("task-list-create")
        self.detail_url = lambda pk: reverse("task-detail", args=[pk])
        self.toggle_url = lambda pk: reverse("task-toggle", args=[pk])

    def test_list_401_sin_autenticacion(self):
        self.client.force_authenticate(user=None)
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_200_y_solo_mis_tasks(self):
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertEqual(data["count"], 5)
        results = data["results"]
        self.assertEqual(len(results), 5)
        ids = {item["id"] for item in results}
        self.assertNotIn(self.other_task.id, ids)

    def test_list_filtrado_completed_true(self):
        resp = self.client.get(self.list_url, {"completed": "true"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        results = data["results"]
        self.assertTrue(all(item["completed"] is True for item in results))

    def test_list_busqueda_por_search(self):
        resp = self.client.get(self.list_url, {"search": "keyword unica"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        results = data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], self.tarea5.id)

    def test_list_ordenamiento_por_title(self):
        resp = self.client.get(self.list_url, {"ordering": "title"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        results = data["results"]
        titles = [item["title"] for item in results]
        self.assertEqual(titles, sorted(titles))

    def test_create_201_asigna_user(self):
        payload = {"title": "Nueva", "description": "desc", "completed": False}
        resp = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        body = resp.json()
        self.assertIn("id", body)
        created = Task.objects.get(pk=body["id"])
        self.assertEqual(created.user_id, self.user.id)
        self.assertEqual(created.title, "Nueva")

    def test_create_400_validacion(self):
        payload = {"description": "sin titulo", "completed": False}
        resp = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_200_propia(self):
        resp = self.client.get(self.detail_url(self.tarea1.id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json()["id"], self.tarea1.id)

    def test_retrieve_404_ajena(self):
        resp = self.client.get(self.detail_url(self.other_task.id))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_put_200(self):
        payload = {"title": "Tarea 1 editada", "description": "d1b", "completed": True}
        resp = self.client.put(self.detail_url(self.tarea1.id), payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.tarea1.refresh_from_db()
        self.assertEqual(self.tarea1.title, "Tarea 1 editada")
        self.assertTrue(self.tarea1.completed)

    def test_update_patch_200(self):
        payload = {"description": "solo patch"}
        resp = self.client.patch(
            self.detail_url(self.tarea2.id), payload, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.tarea2.refresh_from_db()
        self.assertEqual(self.tarea2.description, "solo patch")

    def test_update_404_ajena(self):
        payload = {"title": "no deberia", "description": "x", "completed": True}
        resp = self.client.put(
            self.detail_url(self.other_task.id), payload, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_204(self):
        resp = self.client.delete(self.detail_url(self.tarea3.id))
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=self.tarea3.id).exists())

    def test_delete_404_ajena(self):
        resp = self.client.delete(self.detail_url(self.other_task.id))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_toggle_200_invierte_sin_payload(self):
        self.assertFalse(self.tarea1.completed)
        resp = self.client.patch(self.toggle_url(self.tarea1.id), {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.tarea1.refresh_from_db()
        self.assertTrue(self.tarea1.completed)

    def test_toggle_200_establece_explicito(self):
        resp = self.client.patch(
            self.toggle_url(self.tarea4.id), {"completed": False}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.tarea4.refresh_from_db()
        self.assertFalse(self.tarea4.completed)

    def test_toggle_404_ajena(self):
        resp = self.client.patch(self.toggle_url(self.other_task.id), {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
