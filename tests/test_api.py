import time

from fastapi.testclient import TestClient

from app.main import app


def test_api_agent_history_tasks_and_model_routes() -> None:
    client = TestClient(app)

    created = client.post(
        "/agents",
        json={"name": "worker", "mode": "background", "system_prompt": "go"},
    )
    assert created.status_code == 200
    agent_id = created.json()["id"]

    providers = client.get("/providers")
    assert providers.status_code == 200
    assert "openai_compatible" in providers.json()["providers"]

    caps = client.get("/models/capabilities", params={"provider": "openai_compatible", "model": "local/default"})
    assert caps.status_code == 200
    assert caps.json()["model"] == "local/default"

    generated = client.post(
        "/models/generate",
        json={
            "model": {"provider": "openai_compatible", "model": "local/default"},
            "messages": [{"role": "user", "content": "hi"}],
            "require_capabilities": ["tool_calling"],
            "allow_auto_downgrade": True,
        },
    )
    assert generated.status_code == 200
    assert generated.json()["used_model"] == "gpt-4.1-mini"

    enqueue = client.post("/tasks", json={"agent_id": agent_id, "prompt": "do work"}).json()
    task_id = enqueue["id"]

    status = None
    for _ in range(80):
      status = client.get(f"/tasks/{task_id}").json()
      if status["status"] == "completed":
          break
      time.sleep(0.02)

    assert status is not None
    assert status["status"] == "completed"
    assert status["reasoning_steps"]
    assert status["actions"]

    cleared = client.delete(f"/agents/{agent_id}/history").json()
    assert cleared["status"] == "cleared"
