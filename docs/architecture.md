# Architecture (Bootstrap)

## Scope delivered

This bootstrap focuses on **model interoperability**:

1. Unified request schema (`AgentRequest`)
2. Capability model (`CapabilitySet`)
3. Capability negotiation with explicit downgrade actions (`negotiate_capabilities`)
4. Provider adapter abstraction (`ProviderAdapter`) and initial adapter stubs

## Next milestones

- Add native adapters: OpenAI, Anthropic, Azure, Bedrock, Vertex
- Persist run snapshots and hashed prompt/tool/model config
- Build tool-calling loop and runtime graph execution
- Add policy and secret-management layers
