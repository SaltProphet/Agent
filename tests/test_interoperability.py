import pytest

from app.interoperability import AdapterRegistry, ModelRouter
from app.models import Capability, ConversationMessage, ModelConfig, ProviderType, UnifiedGenerateRequest


def test_capability_fallback_routes_to_stronger_model() -> None:
    router = ModelRouter(AdapterRegistry())
    response = router.generate(
        UnifiedGenerateRequest(
            model=ModelConfig(provider=ProviderType.openai_compatible, model="local/default"),
            messages=[ConversationMessage(role="user", content="hello")],
            require_capabilities=[Capability.tool_calling],
            allow_auto_downgrade=True,
        )
    )
    assert response.used_model == "gpt-4.1-mini"


def test_capability_strict_mode_raises() -> None:
    router = ModelRouter(AdapterRegistry())
    with pytest.raises(ValueError):
        router.generate(
            UnifiedGenerateRequest(
                model=ModelConfig(provider=ProviderType.openai_compatible, model="local/default"),
                messages=[ConversationMessage(role="user", content="hello")],
                require_capabilities=[Capability.tool_calling],
                allow_auto_downgrade=False,
            )
        )
