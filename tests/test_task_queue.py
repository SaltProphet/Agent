import time

from app.agent_manager import AgentManager
from app.interoperability import AdapterRegistry, ModelRouter
from app.models import CreateAgentRequest
from app.task_queue import BackgroundTaskQueue, TaskStatus


def test_background_task_executes_and_records_reasoning() -> None:
    manager = AgentManager()
    router = ModelRouter(AdapterRegistry())
    agent = manager.create_agent(CreateAgentRequest(name="bg", mode="background", model="local/default"))
    q = BackgroundTaskQueue(agent_manager=manager, router=router)
    try:
        task = q.enqueue(agent_id=agent.id, prompt="Run autonomous step")
        for _ in range(60):
            stored = q.get_task(task.id)
            if stored.status == TaskStatus.completed:
                break
            time.sleep(0.02)

        assert stored.status == TaskStatus.completed
        assert stored.reasoning_steps
        assert stored.actions
        assert stored.latency_ms >= 0
        assert stored.tokens_estimate > 0
    finally:
        q.shutdown()
