# To-do list challenge

Aplicación de tareas construida con **Django** y **Django REST Framework**, organizada en tres apps: **api**, **users** y **web**. Autenticación **JWT (Simple JWT)**, filtros avanzados y frontend que consume la API

Las distintas views desarrolladas en este proyecto son Class-Based Views, que ayudan a que el codigo sea mas modular y mantenible, diviendo las responsabilidades de cada funcionalidad (queryset por usuario, permisos, serializador, filtros) y aplicar principio DRY


## Levantar el contendor Docker

```bash
docker-compose up --build

# Con el contenedor corriendo, podemos ejecutar los siguientes comandos funcionales:
docker exec -it todo_challenge pytest # Para correr tests
docker exec -it todo_challenge tail -f /app/logs/django.log # Ver logs en tiempo real
docker exec -it todo_challenge tail -n 20 /app/logs/django.log # Imprimir las ultimas 20 lineas de logs
```

## Apps principales

- **tasks**: Endpoints RESTful que se encargan de manipular el CRUD. Protegida con `IsAuthenticated` y permiso `IsOwner` para asegurar que cada usuario accede solo a sus tareas
- **users**: Manejo de usuarios y endpoints de autenticación **JWT** (obtener/renovar tokens) para acceder a la API
- **web**: Frontend. Usa un **ApiSessionMixin** basado en `requests` para consumir la API. Listados con **django-tables2** y templates con herencia + **Bootstrap**

## Aplicación **tasks** (API)

**Base URL**: `/api/`  

### Endpoints (RESTful)
- **Listar**: `GET /api/`
  - Filtros con **django-filters**:
    - `completed=true|false`
    - `q=<texto>` (búsqueda simple)
    - `created_after=YYYY-MM-DD`
    - `created_before=YYYY-MM-DD`
    - `updated_after=YYYY-MM-DD`
    - `updated_before=YYYY-MM-DD`
  - Ejemplo:
    ```bash
    curl "http://localhost:8000/api/?completed=false&q=comprar"       -H "Authorization: Bearer <access>"
    ```

- **Crear**: `POST /api/`
  ```bash
  curl -X POST http://localhost:8000/api/    -H "Content-Type: application/json"     -H "Authorization: Bearer <access>"     -d '{"title":"Comprar leche","description":"En el super"}'
  ```

- **Detalle**: `GET /api/{id}/`
    ```bash
    curl http://localhost:8000/api/42/ -H "Authorization: Bearer <access>"
    ```

- **Actualizar parcial**: `PATCH /api/{id}/`
  ```bash
  curl -X PATCH http://localhost:8000/api/42/     -H "Content-Type: application/json"     -H "Authorization: Bearer <access>"     -d '{"title": "Example"}'
  ```

- **Eliminar**: `DELETE /api/{id}/`
    ```bash
    curl -X DELETE http://localhost:8000/api/42/ -H "Authorization: Bearer <access>"
    ```

- **Toggle**: `PATCH /api/{id}/toggle/`
  ```bash
  curl -X PATCH http://localhost:8000/api/42/toggle/     -H "Authorization: Bearer <access>"
  ```

### Tests (y mocks)
- **pytest** + **pytest-django** para tests
- **factory_boy** + **Faker** para datos faker de tests
- **Mocks** con `unittest.mock.patch` para aislar lógica (por ejemplo, simular errores de validacion o respuestas de servicios externos cuando aplica)

## Aplicación **web** (Frontend Django)

- **Consumo de API por mixin**: `ApiSessionMixin` centraliza base URL, headers y manejo de tokens usando `requests`
- **Listados con django-tables2**: renderización de tabla de tareas paginada/estilizada
- **Templates**: herencia (layout base) y **Bootstrap** para estilos consistentes

### Tests (y TestCase)
- Pruebas de vistas con `django.test.TestCase` / `pytest-django` verificando:
  - Respuestas HTTP, redirecciones y mensajes
  - Integración del mixin con la sesión y manejo de errores
  - `RequestFactory`/`Client` para simular requests y sesionar tokens