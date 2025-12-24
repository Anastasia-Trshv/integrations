# Lab 4: Message Queue API (RabbitMQ)

## Цель работы
Изучить подход к проектированию API, работающего через асинхронный обмен сообщениями с использованием RabbitMQ.

## Архитектура

Система реализует взаимодействие между Клиентом и Сервером через брокер сообщений RabbitMQ, используя паттерн RPC (Remote Procedure Call).

### Компоненты
1.  **Client**: Публикует запросы в очередь запросов и слушает очередь ответов.
2.  **RabbitMQ**: Брокер сообщений.
3.  **Server**: Слушает очередь запросов, обрабатывает сообщения, выполняет бизнес-логику и отправляет ответ.

### Схема обмена сообщениями

1.  **Request**: Клиент отправляет сообщение в очередь `api.requests`.
    *   `reply_to`: Имя очереди для ответа (временная очередь клиента).
    *   `correlation_id`: Уникальный ID запроса для сопоставления с ответом.
    *   Body: JSON с данными запроса.
2.  **Processing**: Сервер получает сообщение, проверяет аутентификацию, идемпотентность и вызывает соответствующий обработчик.
3.  **Response**: Сервер отправляет результат в очередь, указанную в `reply_to`.
    *   `correlation_id`: Тот же ID, что и в запросе.
    *   Body: JSON с результатом или ошибкой.
4.  **DLQ**: При критических ошибках разбора сообщение отправляется в Dead Letter Queue (`api.dlq`).

## Формат сообщений

### Запрос (Request)
```json
{
  "id": "uuid-v4",
  "version": "v1",
  "action": "create_user",
  "data": {
    "name": "User Name",
    "email": "user@example.com"
  },
  "auth": "api-key-secret"
}
```

### Ответ (Response)
**Успех:**
```json
{
  "correlation_id": "uuid-v4",
  "status": "ok",
  "data": {
    "id": 1,
    "name": "User Name",
    "email": "user@example.com"
  },
  "error": null
}
```

**Ошибка:**
```json
{
  "correlation_id": "uuid-v4",
  "status": "error",
  "data": null,
  "error": "Error description"
}
```

## Реализация

### Аутентификация
Используется простой API Key, передаваемый в поле `auth` сообщения.
*   **Обоснование**: Для внутренней системы обмена сообщениями или изолированной среды это простой и эффективный способ. В продакшене можно использовать JWT, но для лабораторной работы API Key достаточен для демонстрации защиты endpoint-ов.

### Идемпотентность
Реализована проверка уникальности `id` запроса.
*   ID обработанных запросов сохраняются в памяти (или БД).
*   При повторном получении запроса с тем же ID, сервер возвращает ошибку дубликата (или кэшированный ответ).
*   Это предотвращает повторное выполнение операций, изменяющих состояние (создание, удаление).

### Обработка ошибок и надежность
*   **Retry**: RabbitMQ автоматически пытается доставить сообщение, если consumer не подтвердил (ack) получение (в данной реализации используется `auto_ack` или явный ack в блоке `process`).
*   **DLQ**: Если сообщение не может быть разобрано (невалидный JSON), оно отправляется в `api.dlq` для ручного разбора, чтобы не блокировать очередь.
*   **Error Response**: Логические ошибки (не найден, валидация) возвращаются клиенту в поле `error`.

## Запуск

1.  Запустить контейнеры:
    ```bash
    docker-compose up --build
    ```

2.  Запустить клиент (в отдельном терминале, требуется локальный python env или exec в контейнер):
    ```bash
    # Из корневой папки lab4
    pip install -r requirements.txt
    python -m src.client
    ```
    Или внутри контейнера сервера:
    ```bash
    docker-compose exec server python -m src.client
    ```

3. 2025-11-26 05:20:03,069 - __main__ - INFO - Sending request: {'id': '6c5dd0d9-db6b-4ba4-94ed-f21dab586572', 'version': 'v1', 'action': 'create_user', 'data': {'name': 'Test User', 'email': 'test@example.com'}, 'auth': 'dev-secret-key'}
2025-11-26 05:20:03,075 - __main__ - INFO - Received response: {"correlation_id":"6c5dd0d9-db6b-4ba4-94ed-f21dab586572","status":"ok","data":{"id":2,"name":"Test User","email":"test@example.com"},"error":null}
2025-11-26 05:20:03,076 - __main__ - INFO - Response: {"correlation_id":"6c5dd0d9-db6b-4ba4-94ed-f21dab586572","status":"ok","data":{"id":2,"name":"Test User","email":"test@example.com"},"error":null}
2025-11-26 05:20:03,076 - __main__ - INFO - User created: {'id': 2, 'name': 'Test User', 'email': 'test@example.com'}
2025-11-26 05:20:03,076 - __main__ - INFO - Sending request: {'id': '62ec92c1-86fa-48f5-bdb3-f796c13235ff', 'version': 'v1', 'action': 'list_users', 'data': {}, 'auth': 'dev-secret-key'}
2025-11-26 05:20:03,083 - __main__ - INFO - Received response: {"correlation_id":"62ec92c1-86fa-48f5-bdb3-f796c13235ff","status":"ok","data":[{"id":1,"name":"Test User","email":"test@example.com"},{"id":2,"name":"Test User","email":"test@example.com"}],"error":null}
2025-11-26 05:20:03,083 - __main__ - INFO - Response: {"correlation_id":"62ec92c1-86fa-48f5-bdb3-f796c13235ff","status":"ok","data":[{"id":1,"name":"Test User","email":"test@example.com"},{"id":2,"name":"Test User","email":"test@example.com"}],"error":null}

## Сравнение RabbitMQ и REST API

| Характеристика | REST API (HTTP) | RabbitMQ (Message Queue) |
| :--- | :--- | :--- |
| **Связанность** | Синхронная, жесткая связь. Клиент ждет ответа. | Асинхронная, слабая связь. Клиент может не ждать мгновенно. |
| **Надежность** | При падении сервера запрос теряется (если клиент не повторит). | Сообщения сохраняются в очереди до восстановления сервера. |
| **Масштабируемость** | Балансировка нагрузки через Load Balancer. | Легко масштабируется добавлением consumer-ов. |
| **Сложность** | Проще в реализации и отладке. | Требует настройки брокера, сложнее отладка. |
| **Производительность** | Overhead на HTTP handshake. | Высокая пропускная способность, persistent connections. |

Выбор RabbitMQ оправдан для систем, требующих высокой надежности, асинхронной обработки тяжелых задач и слабой связанности компонентов.

