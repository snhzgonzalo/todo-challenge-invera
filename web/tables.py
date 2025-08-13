import django_tables2 as tables


class TaskTable(tables.Table):
    """
    Tabla para renderizar los contenidos obtenidos desde API
    """
    title = tables.Column(verbose_name="Tarea")
    completed = tables.Column(verbose_name="Completada")
    created_at = tables.Column(verbose_name="Creada")
    updated_at = tables.Column(verbose_name="Actualizada")
    acciones = tables.TemplateColumn(
        template_name="web/tasks_action.html",
        verbose_name="Acciones",
        orderable=False,
    )

    def render_completed(self, value):
        return "✅" if bool(value) else "❌"

    class Meta:
        attrs = {"class": "table table-hover table-sm"}
        sequence = ("title", "completed", "created_at", "updated_at", "acciones")
        order_by = "-created_at"
