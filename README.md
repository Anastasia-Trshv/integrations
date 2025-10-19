Tasks API (FastAPI)

Цель
- Учебное REST API c: простотой, стабильностью, версионностью (/api/v1, /api/v2), идемпотентностью, ограничением частоты запросов и документацией (Swagger/OpenAPI).

Предметная область
- Проекты и задачи (kanban-lite):
  - Project: id, name, description
  - Task: id, project_id, title, completed, priority (только v2), user_id (v2)
  - User (v2): id, name, email

```
Дкументация: Swagger UI — http://localhost:8000/docs, OpenAPI JSON — http://localhost:8000/openapi.json

Аутентификация
- API Key в заголовке `X-API-Key`. Значение по умолчанию для разработки: `dev-secret-key` (можно переопределить переменной окружения `API_KEY`).
- Выбор обоснован: просто, прозрачно для сервис-2-сервис, не требует сессий, достаточно для учебного проекта. Для продакшена можно заменить на JWT/OAuth2.

Версионность
- v1: базовые CRUD для `projects` и `tasks`.
- v2: аддитивно добавлено поле `Task.priority` и фильтры для списка задач (`completed`, `priority_min`, `priority_max`). v1 продолжает работать без изменений.
 - v3: добавлена пагинация (`offset`, `limit`) и опциональные поля через `include=user` в `GET /api/v3/tasks/`. Добавлен внутренний API `/internal/metrics`.

Идемпотентность POST
- Заголовок `Idempotency-Key`. Повторный POST с тем же ключом и тем же путём вернёт созданный ранее ресурс без дубликата.
- Техника: middleware перехватывает повтор; обработчики POST сохраняют соответствие ключа к id и выставляют `X-Resource-Id`.

Ограничение частоты запросов (Rate limiting)
- Окно и лимит настраиваются через переменные окружения: `RATE_LIMIT_REQUESTS` (по умолчанию 60), `RATE_LIMIT_WINDOW` (секунды, по умолчанию 60).
- Ответы содержат заголовки: `X-Limit-Remaining` и при превышении `Retry-After`.

Примеры запросов (v2)
```bash
# Создать проект
curl -X POST http://localhost:8000/api/v2/projects/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-secret-key" \
  -H "Idempotency-Key: proj-1" \
  -d '{"name":"Demo","description":"Sample"}'

# Создать задачу с приоритетом
curl -X POST http://localhost:8000/api/v2/tasks/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-secret-key" \
  -H "Idempotency-Key: task-1" \
  -d '{"project_id":1,"title":"Do it","priority":5}'

# Фильтрация задач
curl -X GET "http://localhost:8000/api/v2/tasks/?completed=false&priority_min=3&user_id=1" \
  -H "X-API-Key: dev-secret-key"

# Создать пользователя
curl -X POST http://localhost:8000/api/v2/users/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-secret-key" \
  -H "Idempotency-Key: user-1" \
  -d '{"name":"Alice","email":"alice@example.com"}'
```

Примеры запросов (v3)
```bash
# Пагинация + include
curl -X GET "http://localhost:8000/api/v3/tasks/?offset=0&limit=10&include=user" \
  -H "X-API-Key: dev-secret-key"
```

Ломающие изменения (breaking changes)

ЛР2 — расширения
- Безопасность и лимиты: сохранены API-ключи (`X-API-Key`) и rate limiting с заголовками `X-Limit-Remaining`, `Retry-After`.
- Пагинация: выбрано смещение (`offset`, `limit`) за простоту и предсказуемость для учебной задачи. В `v3` добавлена на `GET /api/v3/tasks/`.
- Опциональные поля: параметр `include=user` в `v3` позволяет по требованию вернуть вложенного пользователя задачи, чтобы экономить трафик по умолчанию.
- Внутренний API: `GET /internal/metrics` отдаёт агрегированные метрики. Защита через заголовок `X-Internal-Token` (по умолчанию `dev-internal`), упрощения допустимы, так как эндпоинт не публичный.
- Переименование/удаление полей, изменение типов, изменение семантики ответов, смена путей, изменение кода статусов — всё это ломает клиентов. Такие изменения следует выпускать только в новой версии (`/api/v3`) и поддерживать старые версии до миграции клиентов.

Структура
```
src/
  main.py
  app/
    core/ (config, auth, storage)
    middlewares/ (rate_limit, idempotency)
    schemas/ (pydantic-модели)
    api/
      v1/ (projects, tasks)
      v2/ (projects, tasks)
```
