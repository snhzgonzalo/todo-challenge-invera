import json
import pytest
import requests
from django.test import TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.storage.fallback import FallbackStorage
from unittest.mock import patch
from web.mixins import ApiSessionMixin

pytestmark = pytest.mark.django_db


class TestApiSessionMixinUnit(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.m = ApiSessionMixin()

    def make_request(self, path="/", access=None, refresh=None):
        request = self.factory.get(path)
        SessionMiddleware(lambda r: None).process_request(request)
        if access is not None:
            request.session["access"] = access
        if refresh is not None:
            request.session["refresh"] = refresh
        request.session.save()
        setattr(request, "_messages", FallbackStorage(request))
        return request

    def make_response(self, status=200, data=None):
        response = requests.Response()
        response.status_code = status
        response.headers["Content-Type"] = "application/json"
        response._content = b"" if data is None else json.dumps(data).encode()
        return response

    def test_get_headers_sin_token_required_none(self):
        request = self.make_request("/")
        headers = self.m.get_headers(request, token_required=True)
        self.assertIsNone(headers)

    def test_get_headers_con_token(self):
        request = self.make_request("/", access="A")
        headers = self.m.get_headers(request, token_required=True)
        self.assertEqual(headers.get("Authorization"), "Bearer A")

    def test_api_request_exito(self):
        request = self.make_request("/", access="A")
        with patch(
            "web.mixins.requests.request",
            return_value=self.make_response(200, {"ok": True}),
        ) as mocked:
            response = self.m.api_request("GET", "/x", request, success_msg="ok")
        self.assertIsInstance(response, requests.Response)
        self.assertEqual(response.status_code, 200)
        mocked.assert_called()

    def test_api_request_error_400(self):
        request = self.make_request("/", access="A")
        with patch(
            "web.mixins.requests.request",
            return_value=self.make_response(400, {"detail": "bad"}),
        ) as mocked:
            response = self.m.api_request("GET", "/x", request, error_msg="err")
        self.assertIsInstance(response, requests.Response)
        self.assertEqual(response.status_code, 400)
        mocked.assert_called()

    def test_api_request_excepcion_retorna_none(self):
        request = self.make_request("/", access="A")
        with patch(
            "web.mixins.requests.request", side_effect=requests.RequestException("boom")
        ):
            response = self.m.api_request("GET", "/x", request)
        self.assertIsNone(response)

    def test_refresh_token_inexistente_flush(self):
        request = self.make_request("/", access="A")
        self.m.refresh_token(request)
        self.assertFalse(list(request.session.keys()))

    def test_401_refresca_y_reintenta(self):
        request = self.make_request("/", access="OLD", refresh="REF")
        first = self.make_response(401, {})
        second = self.make_response(200, {"ok": True})
        refresh_resp = self.make_response(200, {"access": "NEW", "refresh": "REF"})
        calls = []

        def fake_request(
            method, url, json=None, headers=None, params=None, timeout=None
        ):
            calls.append({"m": method, "h": dict(headers or {})})
            return first if len(calls) == 1 else second

        with (
            patch("web.mixins.requests.post", return_value=refresh_resp),
            patch("web.mixins.requests.request", side_effect=fake_request),
        ):
            response = self.m.api_request("GET", "/x", request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(calls[0]["h"].get("Authorization"), "Bearer OLD")
        self.assertEqual(calls[1]["h"].get("Authorization"), "Bearer NEW")
