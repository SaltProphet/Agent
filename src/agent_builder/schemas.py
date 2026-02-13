from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class CapabilitySet:
    tool_calling: bool = False
    structured_output: bool = False
    vision: bool = False
    audio: bool = False
    image_generation: bool = False
    embeddings: bool = False
    reasoning_tokens: bool = False
    streaming: bool = True
    parallel_tool_calls: bool = False
    max_context_tokens: int = 8192
    max_output_tokens: int = 1024


@dataclass(frozen=True)
class RequestedBehavior:
    require_tool_calling: bool = False
    require_structured_output: bool = False
    require_streaming: bool = False
    planner_executor_fallback_allowed: bool = True


@dataclass(frozen=True)
class AgentRequest:
    model: str
    provider: str
    input_text: str
    output_mode: Literal["text", "json"] = "text"


@dataclass
class DegradationPlan:
    accepted: bool
    actions: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
