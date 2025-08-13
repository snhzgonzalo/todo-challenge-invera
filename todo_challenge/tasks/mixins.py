class TaskOwnedQuerysetMixin:
    """Filtra el queryset para mostrar solo las tareas del usuario autenticado."""
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)