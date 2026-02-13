import time

from fastapi.testclient import TestClient

from app.main import app


def test_api_agent_history_and_tasks() -> None:
    client = TestClient(app)

    created = client.post(
        "/agents",
        json={"name": "worker", "mode": "background", "system_prompt": "go"},
    ).json()
    agent_id = created["id"]

    enqueue = client.post("/tasks", json={"agent_id": agent_id, "prompt": "do work"}).json()
    task_id = enqueue["id"]

    status = None
    for _ in range(50):
        status = client.get(f"/tasks/{task_id}").json()
        if status["status"] == "completed":
            break
        time.sleep(0.02)

    assert status is not None
    assert status["status"] == "completed"
    assert status["reasoning_steps"]

    cleared = client.delete(f"/agents/{agent_id}/history").json()
    assert cleared["status"] == "cleared"
