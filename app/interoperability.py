from __future__ import annotations

from dataclasses import dataclass

from app.models import (
    Capability,
    CapabilityProfile,
    ConversationMessage,
    ModelConfig,
    ProviderType,
    UnifiedGenerateRequest,
    UnifiedGenerateResponse,
)


@dataclass
class ProviderAdapter:
    provider: ProviderType

    def transform_messages(self, messages: list[ConversationMessage]) -> list[dict[str, str]]:
        return [{"role": m.role, "content": m.content} for m in messages]

    def generate(self, model: str, messages: list[ConversationMessage]) -> str:
        last = messages[-1].content if messages else ""
        return f"[{self.provider.value}:{model}] {last}".strip()


class OpenAICompatibleAdapter(ProviderAdapter):
    def __init__(self) -> None:
        super().__init__(provider=ProviderType.openai_compatible)


class AdapterRegistry:
    def __init__(self) -> None:
        self._adapters = {
            ProviderType.openai: ProviderAdapter(ProviderType.openai),
            ProviderType.anthropic: ProviderAdapter(ProviderType.anthropic),
            ProviderType.azure: ProviderAdapter(ProviderType.azure),
            ProviderType.bedrock: ProviderAdapter(ProviderType.bedrock),
            ProviderType.vertex: ProviderAdapter(ProviderType.vertex),
            ProviderType.openai_compatible: OpenAICompatibleAdapter(),
            ProviderType.generic_rest: ProviderAdapter(ProviderType.generic_rest),
        }
        self._profiles = {
            "local/default": CapabilityProfile(
                provider=ProviderType.openai_compatible,
                model="local/default",
                context_length=8192,
                max_output_tokens=1024,
                capabilities=[Capability.streaming, Capability.structured_output],
            ),
            "gpt-4.1-mini": CapabilityProfile(
                provider=ProviderType.openai,
                model="gpt-4.1-mini",
                context_length=128000,
                max_output_tokens=8192,
                capabilities=[
                    Capability.streaming,
                    Capability.structured_output,
                    Capability.tool_calling,
                    Capability.parallel_tool_calls,
                    Capability.reasoning_tokens,
                ],
            ),
        }


    def list_providers(self) -> list[ProviderType]:
        return list(self._adapters.keys())
    def get_adapter(self, provider: ProviderType) -> ProviderAdapter:
        return self._adapters[provider]

    def discover_capabilities(self, model: ModelConfig) -> CapabilityProfile:
        return self._profiles.get(
            model.model,
            CapabilityProfile(provider=model.provider, model=model.model),
        )


class ModelRouter:
    def __init__(self, registry: AdapterRegistry) -> None:
        self._registry = registry

    def negotiate_capabilities(self, request: UnifiedGenerateRequest) -> tuple[CapabilityProfile, list[Capability]]:
        profile = self._registry.discover_capabilities(request.model)
        missing = [cap for cap in request.require_capabilities if cap not in profile.capabilities]
        if missing and not request.allow_auto_downgrade:
            raise ValueError(f"Missing required capabilities: {[m.value for m in missing]}")
        return profile, missing

    def generate(self, request: UnifiedGenerateRequest) -> UnifiedGenerateResponse:
        profile, missing = self.negotiate_capabilities(request)
        selected_model = request.model.model
        selected_provider = request.model.provider

        # simple fallback policy: if capabilities missing, route to stronger default model
        if missing:
            selected_model = "gpt-4.1-mini"
            selected_provider = ProviderType.openai
            profile = self._registry.discover_capabilities(
                ModelConfig(provider=selected_provider, model=selected_model)
            )

        adapter = self._registry.get_adapter(selected_provider)
        output = adapter.generate(model=selected_model, messages=request.messages)
        return UnifiedGenerateResponse(
            output_text=output,
            used_provider=selected_provider,
            used_model=selected_model,
            downgraded_capabilities=missing,
            metadata={
                "context_length": profile.context_length,
                "max_output_tokens": profile.max_output_tokens,
                "capabilities": [c.value for c in profile.capabilities],
            },
        )
