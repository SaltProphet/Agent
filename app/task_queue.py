from __future__ import annotations

import queue
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List
from uuid import uuid4

from app.agent_manager import AgentManager
from app.interoperability import ModelRouter
from app.models import Capability, ConversationMessage, ModelConfig, UnifiedGenerateRequest


class TaskStatus(str, Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"


@dataclass
class TaskState:
    id: str
    agent_id: str
    prompt: str
    status: TaskStatus = TaskStatus.queued
    result: str | None = None
    error: str | None = None
    reasoning_steps: List[str] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)
    tokens_estimate: int = 0
    latency_ms: int = 0


class BackgroundTaskQueue:
    def __init__(self, agent_manager: AgentManager, router: ModelRouter) -> None:
        self._agent_manager = agent_manager
        self._router = router
        self._q: queue.Queue[str] = queue.Queue()
        self._tasks: Dict[str, TaskState] = {}
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._worker = threading.Thread(target=self._run, daemon=True)
        self._worker.start()

    def enqueue(self, agent_id: str, prompt: str) -> TaskState:
        self._agent_manager.get_agent(agent_id)
        task = TaskState(id=str(uuid4()), agent_id=agent_id, prompt=prompt)
        with self._lock:
            self._tasks[task.id] = task
        self._q.put(task.id)
        return task

    def get_task(self, task_id: str) -> TaskState:
        with self._lock:
            if task_id not in self._tasks:
                raise KeyError(f"Task {task_id} not found")
            return self._tasks[task_id]

    def shutdown(self) -> None:
        self._stop.set()
        self._q.put("__STOP__")
        self._worker.join(timeout=2)

    def _run(self) -> None:
        while not self._stop.is_set():
            task_id = self._q.get()
            if task_id == "__STOP__":
                return
            self._execute(task_id)

    def _execute(self, task_id: str) -> None:
        start = time.perf_counter()
        with self._lock:
            task = self._tasks[task_id]
            task.status = TaskStatus.running
            task.reasoning_steps.append("Load agent definition and conversation context")
            task.actions.append("fetch_agent")

        try:
            agent = self._agent_manager.get_agent(task.agent_id)
            history = self._agent_manager.get_history(task.agent_id)

            messages = [ConversationMessage(role="system", content=agent.system_prompt)] + history + [
                ConversationMessage(role="user", content=task.prompt)
            ]
            task.reasoning_steps.append("Negotiate model capabilities and fallback if needed")
            task.actions.append("capability_negotiation")

            response = self._router.generate(
                UnifiedGenerateRequest(
                    model=ModelConfig(provider=agent.provider, model=agent.model),
                    messages=messages,
                    require_capabilities=[Capability.streaming, Capability.structured_output],
                    allow_auto_downgrade=True,
                )
            )

            self._agent_manager.add_message(task.agent_id, role="user", content=task.prompt)
            self._agent_manager.add_message(task.agent_id, role="assistant", content=response.output_text)

            elapsed_ms = int((time.perf_counter() - start) * 1000)
            with self._lock:
                task.reasoning_steps.append("Persist assistant output and run trace")
                task.actions.append("write_conversation")
                task.result = response.output_text
                task.tokens_estimate = sum(len(m.content.split()) for m in messages)
                task.latency_ms = elapsed_ms
                task.status = TaskStatus.completed
        except Exception as exc:  # pragma: no cover
            with self._lock:
                task.error = str(exc)
                task.status = TaskStatus.failed
