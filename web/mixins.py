import requests
import logging

from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings

logger = logging.getLogger(__name__)


class SessionRequiredMixin:
    """
    Exige sesión en cualquier CBV protegida.
    Evita que se renderice la vista vacía si no hay token.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get("access"):
            messages.error(request, "Debe iniciar sesión para continuar.")
            return redirect("web:login")
        return super().dispatch(request, *args, **kwargs)


class ApiSessionMixin:
    """
    Interactua con la api a traves de requests.
    """
    api_base = getattr(settings, "API_BASE_URL", "http://localhost:8000/api").rstrip("/")
    refresh_path = getattr(settings, "API_REFRESH_PATH", "/auth/token/refresh/")
    timeout = getattr(settings, "API_TIMEOUT", 6)

    def build_url(self, path):
        return f"{self.api_base}/{str(path).lstrip('/')}"

    def get_token(self, request, required=True):
        token = request.session.get("access")
        if required and not token:
            messages.error(request, "Debe iniciar sesión para continuar.")
        return token

    def get_headers(self, request, token_required):
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        if token_required:
            token = self.get_token(request, required=True)
            if not token:
                return None
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def save_tokens(self, request, data):
        if data.get("access"):
            request.session["access"] = data.get("access")
        if data.get("refresh"):
            request.session["refresh"] = data.get("refresh")

    def refresh_token(self, request):
        refresh = request.session.get("refresh")
        if not refresh:
            request.session.flush()
            return

        try:
            resp = requests.post(
                self.build_url(self.refresh_path),
                json={"refresh": refresh},
                timeout=self.timeout,
                headers={"Accept": "application/json", "Content-Type": "application/json"},
            )
        except requests.RequestException:
            return

        if resp.status_code == 200:
            try:
                self.save_tokens(request, resp.json())
            except ValueError:
                request.session.flush()
        else:
            request.session.flush()

    def api_request(
        self,
        method,
        path,
        request,
        data=None,
        token_required=True,
        success_msg=None,
        error_msg=None,
        params=None,
    ):
        headers = self.get_headers(request, token_required)
        if token_required and headers is None:
            return redirect("web:login")

        url = self.build_url(path)
        logger.info(f"WEB → API {method} {url}")
        try:
            response = requests.request(
                method,
                url,
                json=data,
                headers=headers,
                params=params,
                timeout=self.timeout
            )
        except requests.RequestException:
            logger.error(f"WEB → API ERROR {method} {url}")
            messages.error(request, "Error de conexión con el servidor.")
            return None
        if response.status_code == 401 and token_required:
            self.refresh_token(request)
            headers = self.get_headers(request, token_required=True)
            if headers is None:
                return redirect("web:login")
            try:
                response = requests.request(
                    method,
                    url,
                    json=data,
                    headers=headers,
                    params=params,
                    timeout=self.timeout
                )
            except requests.RequestException:
                logger.error(f"WEB → API ERROR {method} {url}")
                messages.error(request, "Error de conexión con el servidor.")
                return None
        if 200 <= response.status_code < 300:
            logger.info(f"API → WEB {response.status_code} {method} {url}")
            if success_msg:
                messages.success(request, success_msg)
        else:
            logger.warning(f"API → WEB {response.status_code} {method} {url}")
            messages.error(request, error_msg or f"Error ({response.status_code})")

        return response
