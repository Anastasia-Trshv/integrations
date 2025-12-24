from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Dict, Optional


_id_lock = threading.Lock()


def _next_id(counter: Dict[str, int], key: str) -> int:
    with _id_lock:
        counter[key] = counter.get(key, 0) + 1
        return counter[key]


@dataclass
class Project:
    id: int
    name: str
    description: str = ""


@dataclass
class Task:
    id: int
    project_id: int
    title: str
    completed: bool = False
    # v2 additive field
    priority: Optional[int] = None
    # v2 additive linkage to user
    user_id: Optional[int] = None


@dataclass
class User:
    id: int
    name: str
    email: str


@dataclass
class InMemoryDB:
    projects: Dict[int, Project] = field(default_factory=dict)
    tasks: Dict[int, Task] = field(default_factory=dict)
    users: Dict[int, User] = field(default_factory=dict)
    id_counters: Dict[str, int] = field(default_factory=dict)
    idempotency: Dict[str, int] = field(default_factory=dict)  # key -> created resource id

    def create_project(self, name: str, description: str = "") -> Project:
        new_id = _next_id(self.id_counters, "project")
        project = Project(id=new_id, name=name, description=description)
        self.projects[new_id] = project
        return project

    def create_task(self, project_id: int, title: str, completed: bool = False, priority: Optional[int] = None) -> Task:
        new_id = _next_id(self.id_counters, "task")
        task = Task(id=new_id, project_id=project_id, title=title, completed=completed, priority=priority)
        self.tasks[new_id] = task
        return task

    def create_task_v2(
        self,
        project_id: int,
        title: str,
        completed: bool = False,
        priority: Optional[int] = None,
        user_id: Optional[int] = None,
    ) -> Task:
        new_id = _next_id(self.id_counters, "task")
        task = Task(
            id=new_id,
            project_id=project_id,
            title=title,
            completed=completed,
            priority=priority,
            user_id=user_id,
        )
        self.tasks[new_id] = task
        return task

    def create_user(self, name: str, email: str) -> User:
        new_id = _next_id(self.id_counters, "user")
        user = User(id=new_id, name=name, email=email)
        self.users[new_id] = user
        return user


db = InMemoryDB()

