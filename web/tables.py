import django_tables2 as tables
from django.utils.dateparse import parse_datetime
from django.utils.timezone import localtime


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

    def format_local_datetime(self, value):
        date = parse_datetime(value) if isinstance(value, str) else value
        return localtime(date).strftime("%d-%m-%Y %H:%M") if date else ""

    def render_created_at(self, value):
        return self.format_local_datetime(value)

    def render_updated_at(self, value):
        return self.format_local_datetime(value)

    class Meta:
        attrs = {
            "class": "table table-hover table-sm text-center align-middle",
            "th": {"class": "text-center align-middle"},
            "td": {"class": "text-center align-middle"},
        }
        sequence = ("title", "completed", "created_at", "updated_at", "acciones")
        order_by = "-created_at"
