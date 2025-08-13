import logging

from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import RegisterSerializer

logger = logging.getLogger(__name__)


class RegisterView(generics.CreateAPIView):
    """
    Permite registrar un nuevo usuario.
    Retorna 201 si el registro fue exitoso.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        logger.info("API users register")
        return Response(
            {"detail": "Usuario registrado correctamente."},
            status=status.HTTP_201_CREATED
        )