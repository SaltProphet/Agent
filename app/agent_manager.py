from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock
from typing import Dict, List
from uuid import uuid4

from app.models import AgentDefinition, ConversationMessage, CreateAgentRequest


@dataclass
class AgentState:
    definition: AgentDefinition
    conversation: List[ConversationMessage] = field(default_factory=list)
    scratchpad: list[str] = field(default_factory=list)
    pinned_facts: dict[str, str] = field(default_factory=dict)


class AgentManager:
    def __init__(self) -> None:
        self._lock = Lock()
        self._agents: Dict[str, AgentState] = {}

    def create_agent(self, request: CreateAgentRequest) -> AgentDefinition:
        agent_id = str(uuid4())
        definition = AgentDefinition(
            id=agent_id,
            name=request.name,
            system_prompt=request.system_prompt,
            goals=request.goals,
            constraints=request.constraints,
            mode=request.mode,
            model=request.model,
            provider=request.provider,
            allowed_tools=request.allowed_tools,
            network_allowlist=request.network_allowlist,
            budget_tokens=request.budget_tokens,
            budget_seconds=request.budget_seconds,
        )
        with self._lock:
            self._agents[agent_id] = AgentState(definition=definition)
        return definition

    def list_agents(self) -> List[AgentDefinition]:
        with self._lock:
            return [state.definition for state in self._agents.values()]

    def add_message(self, agent_id: str, role: str, content: str) -> ConversationMessage:
        message = ConversationMessage(role=role, content=content)
        with self._lock:
            self._require_agent(agent_id).conversation.append(message)
        return message

    def get_history(self, agent_id: str) -> List[ConversationMessage]:
        with self._lock:
            return list(self._require_agent(agent_id).conversation)

    def clear_history(self, agent_id: str) -> None:
        with self._lock:
            self._require_agent(agent_id).conversation.clear()

    def get_agent(self, agent_id: str) -> AgentDefinition:
        with self._lock:
            return self._require_agent(agent_id).definition

    def _require_agent(self, agent_id: str) -> AgentState:
        if agent_id not in self._agents:
            raise KeyError(f"Agent {agent_id} not found")
        return self._agents[agent_id]
