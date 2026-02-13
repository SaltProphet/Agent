from __future__ import annotations

from abc import ABC, abstractmethod

from .schemas import AgentRequest, CapabilitySet


class ProviderAdapter(ABC):
    """Base adapter contract for all model providers."""

    name: str

    @abstractmethod
    def discover_capabilities(self, model: str) -> CapabilitySet:
        raise NotImplementedError

    @abstractmethod
    def send(self, request: AgentRequest) -> dict:
        raise NotImplementedError


class OpenAICompatibleAdapter(ProviderAdapter):
    """Adapter for OpenAI-style endpoints, including local runtimes."""

    name = "openai_compatible"

    def discover_capabilities(self, model: str) -> CapabilitySet:
        return CapabilitySet(
            tool_calling=True,
            structured_output=True,
            streaming=True,
            parallel_tool_calls=True,
            max_context_tokens=128000,
            max_output_tokens=4096,
        )

    def send(self, request: AgentRequest) -> dict:
        return {
            "provider": self.name,
            "model": request.model,
            "echo": request.input_text,
            "status": "stubbed",
        }


class GenericRESTAdapter(ProviderAdapter):
    """Fallback adapter for vendor endpoints without native integration."""

    name = "generic_rest"

    def discover_capabilities(self, model: str) -> CapabilitySet:
        return CapabilitySet()

    def send(self, request: AgentRequest) -> dict:
        return {
            "provider": self.name,
            "model": request.model,
            "echo": request.input_text,
            "status": "stubbed",
        }
