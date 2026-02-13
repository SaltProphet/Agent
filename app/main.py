from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from app.agent_manager import AgentManager
from app.interoperability import AdapterRegistry, ModelRouter
from app.models import (
    ModelConfig,
    CreateAgentRequest,
    ProviderType,
    QueueTaskRequest,
    ToolExecutionRequest,
    UnifiedGenerateRequest,
)
from app.task_queue import BackgroundTaskQueue
from app.tool_runtime import UnsafeCodeError, execute_tool

BASE_DIR = Path(__file__).resolve().parent

# Module-level instances that will be initialized in lifespan
registry = AdapterRegistry()
router = ModelRouter(registry=registry)
manager = AgentManager()
task_queue: BackgroundTaskQueue | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage BackgroundTaskQueue lifecycle to prevent thread leaks."""
    global task_queue
    task_queue = BackgroundTaskQueue(agent_manager=manager, router=router)
    yield
    task_queue.shutdown()


app = FastAPI(title="Local Agent Creator", lifespan=lifespan)


@app.get("/")
def index() -> FileResponse:
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/agents")
def create_agent(request: CreateAgentRequest):
    return manager.create_agent(request).model_dump()


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
    if task_queue is None:
        raise HTTPException(status_code=503, detail="Task queue not initialized")
    try:
        task = task_queue.enqueue(agent_id=request.agent_id, prompt=request.prompt)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"id": task.id, "status": task.status}


@app.get("/tasks/{task_id}")
def get_task(task_id: str):
    if task_queue is None:
        raise HTTPException(status_code=503, detail="Task queue not initialized")
    try:
        task = task_queue.get_task(task_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {
        "id": task.id,
        "status": task.status,
        "result": task.result,
        "error": task.error,
        "reasoning_steps": task.reasoning_steps,
        "actions": task.actions,
        "tokens_estimate": task.tokens_estimate,
        "latency_ms": task.latency_ms,
    }


@app.post("/tools/execute")
def execute_tool_endpoint(request: ToolExecutionRequest):
    try:
        result = execute_tool(request.language, request.code, request.timeout_seconds)
    except UnsafeCodeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=f"Runtime not installed: {exc}") from exc
    return {"stdout": result.stdout, "stderr": result.stderr, "exit_code": result.exit_code}


@app.get("/models/capabilities")
def get_capabilities(provider: str, model: str):
    profile = registry.discover_capabilities(ModelConfig(provider=ProviderType(provider), model=model))
    return profile.model_dump()


@app.post("/models/generate")
def generate(request: UnifiedGenerateRequest):
    try:
        response = router.generate(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return response.model_dump()


@app.get("/providers")
def list_providers():
    return {"providers": [p.value for p in registry.list_providers()]}
