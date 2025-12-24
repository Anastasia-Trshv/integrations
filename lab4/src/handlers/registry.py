from typing import Callable, Dict, Any

from src.handlers.v1 import projects as projects_v1
from src.handlers.v1 import tasks as tasks_v1
from src.handlers.v1 import users as users_v1

# Handler signature: (data: dict) -> Any
HandlerFunc = Callable[[Dict[str, Any]], Any]

_handlers: Dict[str, Dict[str, HandlerFunc]] = {
    "v1": {
        "create_project": projects_v1.create_project,
        "list_projects": projects_v1.list_projects,
        "get_project": projects_v1.get_project,
        "update_project": projects_v1.update_project,
        "delete_project": projects_v1.delete_project,
        "create_task": tasks_v1.create_task,
        "list_tasks": tasks_v1.list_tasks,
        "get_task": tasks_v1.get_task,
        "update_task": tasks_v1.update_task,
        "delete_task": tasks_v1.delete_task,
        "create_user": users_v1.create_user,
        "list_users": users_v1.list_users,
        "get_user": users_v1.get_user,
        "update_user": users_v1.update_user,
        "delete_user": users_v1.delete_user,
    }
}

def get_handler(version: str, action: str) -> HandlerFunc | None:
    return _handlers.get(version, {}).get(action)

