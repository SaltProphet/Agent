from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


class AgentMode(str, Enum):
    local = "local"
    background = "background"


class ConversationMessage(BaseModel):
    role: str
    content: str


class AgentDefinition(BaseModel):
    id: str
    name: str
    system_prompt: str = ""
    mode: AgentMode = AgentMode.local
    model: str = "openai-compatible/local"


class CreateAgentRequest(BaseModel):
    name: str = Field(min_length=1)
    system_prompt: str = ""
    mode: AgentMode = AgentMode.local
    model: str = "openai-compatible/local"


class ToolExecutionRequest(BaseModel):
    language: str = Field(pattern="^(python|javascript)$")
    code: str = Field(min_length=1)
    timeout_seconds: int = Field(default=5, ge=1, le=30)


class QueueTaskRequest(BaseModel):
    agent_id: str
    prompt: str = Field(min_length=1)
