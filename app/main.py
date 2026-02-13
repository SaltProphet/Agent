from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

from app.agent_manager import AgentManager
from app.models import CreateAgentRequest, QueueTaskRequest, ToolExecutionRequest
from app.task_queue import BackgroundTaskQueue
from app.tool_runtime import UnsafeCodeError, execute_tool

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Local Agent Creator")
manager = AgentManager()
queue = BackgroundTaskQueue(agent_manager=manager)


@app.get("/")
def index() -> FileResponse:
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.post("/agents")
def create_agent(request: CreateAgentRequest):
    agent = manager.create_agent(
        name=request.name,
        system_prompt=request.system_prompt,
        mode=request.mode,
        model=request.model,
    )
    return agent.model_dump()


@app.get("/agents")
def list_agents():
    return [agent.model_dump() for agent in manager.list_agents()]


@app.get("/agents/{agent_id}/history")
def get_history(agent_id: str):
    try:
        return [m.model_dump() for m in manager.get_history(agent_id)]
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.delete("/agents/{agent_id}/history")
def clear_history(agent_id: str):
    try:
        manager.clear_history(agent_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"status": "cleared", "agent_id": agent_id}


@app.post("/tasks")
def enqueue_task(request: QueueTaskRequest):
    try:
        task = queue.enqueue(agent_id=request.agent_id, prompt=request.prompt)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {
        "id": task.id,
        "status": task.status,
    }


@app.get("/tasks/{task_id}")
def get_task(task_id: str):
    try:
        task = queue.get_task(task_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {
        "id": task.id,
        "status": task.status,
        "result": task.result,
        "error": task.error,
        "reasoning_steps": task.reasoning_steps,
        "actions": task.actions,
    }


@app.post("/tools/execute")
def execute_tool_endpoint(request: ToolExecutionRequest):
    try:
        result = execute_tool(
            language=request.language,
            code=request.code,
            timeout_seconds=request.timeout_seconds,
        )
    except UnsafeCodeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=f"Runtime not installed: {exc}") from exc
    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "exit_code": result.exit_code,
    }
