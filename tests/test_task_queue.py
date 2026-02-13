import time

from app.agent_manager import AgentManager
from app.models import AgentMode
from app.task_queue import BackgroundTaskQueue, TaskStatus


def test_background_task_executes_and_records_reasoning() -> None:
    manager = AgentManager()
    agent = manager.create_agent("bg", "", AgentMode.background, "local")
    q = BackgroundTaskQueue(agent_manager=manager)
    try:
        task = q.enqueue(agent_id=agent.id, prompt="Run autonomous step")
        for _ in range(50):
            stored = q.get_task(task.id)
            if stored.status == TaskStatus.completed:
                break
            time.sleep(0.02)

        assert stored.status == TaskStatus.completed
        assert stored.reasoning_steps
        assert stored.actions
        assert "Processed prompt" in (stored.result or "")
    finally:
        q.shutdown()
