from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AgentMode(str, Enum):
    local = "local"
    background = "background"


class Capability(str, Enum):
    tool_calling = "tool_calling"
    structured_output = "structured_output"
    vision = "vision"
    audio = "audio"
    image_generation = "image_generation"
    embeddings = "embeddings"
    reasoning_tokens = "reasoning_tokens"
    streaming = "streaming"
    parallel_tool_calls = "parallel_tool_calls"


class ProviderType(str, Enum):
    openai = "openai"
    anthropic = "anthropic"
    azure = "azure"
    bedrock = "bedrock"
    vertex = "vertex"
    openai_compatible = "openai_compatible"
    generic_rest = "generic_rest"


class ConversationMessage(BaseModel):
    role: str
    content: str


class AgentDefinition(BaseModel):
    id: str
    name: str
    system_prompt: str = ""
    goals: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    mode: AgentMode = AgentMode.local
    model: str = "local/default"
    provider: ProviderType = ProviderType.openai_compatible
    allowed_tools: list[str] = Field(default_factory=list)
    network_allowlist: list[str] = Field(default_factory=list)
    budget_tokens: int = 20_000
    budget_seconds: int = 120


class CreateAgentRequest(BaseModel):
    name: str = Field(min_length=1)
    system_prompt: str = ""
    goals: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    mode: AgentMode = AgentMode.local
    model: str = "local/default"
    provider: ProviderType = ProviderType.openai_compatible
    allowed_tools: list[str] = Field(default_factory=list)
    network_allowlist: list[str] = Field(default_factory=list)
    budget_tokens: int = Field(default=20_000, ge=100, le=10_000_000)
    budget_seconds: int = Field(default=120, ge=5, le=3600)


class ToolExecutionRequest(BaseModel):
    language: str = Field(pattern="^(python|javascript)$")
    code: str = Field(min_length=1)
    timeout_seconds: int = Field(default=5, ge=1, le=30)


class QueueTaskRequest(BaseModel):
    agent_id: str
    prompt: str = Field(min_length=1)


class ModelConfig(BaseModel):
    provider: ProviderType
    model: str
    base_url: str | None = None
    cost_tier: str = "standard"
    latency_tier: str = "balanced"
    region: str | None = None


class CapabilityProfile(BaseModel):
    provider: ProviderType
    model: str
    context_length: int = 8192
    max_output_tokens: int = 2048
    capabilities: list[Capability] = Field(default_factory=list)


class UnifiedGenerateRequest(BaseModel):
    model: ModelConfig
    messages: list[ConversationMessage] = Field(default_factory=list)
    require_capabilities: list[Capability] = Field(default_factory=list)
    allow_auto_downgrade: bool = True
    output_schema: dict[str, Any] | None = None


class UnifiedGenerateResponse(BaseModel):
    output_text: str
    used_provider: ProviderType
    used_model: str
    downgraded_capabilities: list[Capability] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
