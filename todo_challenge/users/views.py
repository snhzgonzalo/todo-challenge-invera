from rest_framework import generics
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from .serializers import RegisterSerializer


class RegisterView(generics.CreateAPIView):
    """
    Permite registrar un nuevo usuario.
    Retorna 201 si el registro fue exitoso.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(
            {"detail": "Usuario registrado correctamente."},
            status=status.HTTP_201_CREATED
        )