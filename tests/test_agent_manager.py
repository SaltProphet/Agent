from app.agent_manager import AgentManager
from app.models import AgentMode


def test_create_and_clear_history() -> None:
    manager = AgentManager()
    agent = manager.create_agent("demo", "sys", AgentMode.local, "local-model")

    manager.add_message(agent.id, "user", "hello")
    assert len(manager.get_history(agent.id)) == 1

    manager.clear_history(agent.id)
    assert manager.get_history(agent.id) == []
