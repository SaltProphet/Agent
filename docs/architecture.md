# Architecture Ownership Map

## Feature buckets and ownership

- **Prompt building, chat UX, run controls** → `apps/builder-ui`
- **Run graph execution, scheduling, retries, resumability** → `services/orchestrator`
- **Model/provider abstraction, capability negotiation, adapter routing** → `services/model-gateway`
- **Tool plugin onboarding, schema and version governance** → `services/tool-registry`
- **Tracing, metrics, usage, cost accounting** → `services/observability`
- **RBAC, secrets boundaries, egress and policy controls** → `services/policy`
- **Canonical cross-service contracts and capability model** → `packages/contracts`

## Cross-cutting boundaries

- `packages/contracts` is the shared source of truth for payloads and metadata.
- `services/orchestrator` depends on `services/model-gateway`, `services/tool-registry`, and `services/policy` at runtime.
- `services/observability` receives event streams from all services.
