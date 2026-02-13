# Roadmap

## Phase 1: Foundation

- Initialize monorepo and package boundaries.
- Add baseline CI quality gates (lint/typecheck/test).
- Establish shared contracts for messages, capabilities, and run snapshots.

## Phase 2: Primitives

- Implement model gateway adapters and capability negotiation.
- Implement tool manifest and schema validation pipeline.
- Implement policy enforcement interfaces.

## Phase 3: Runtime

- Expand orchestrator graph runtime with durable checkpoints.
- Integrate retries and typed error handling across model/tool/policy boundaries.
- Add observability pipelines for traces, metrics, and per-run cost accounting.

## Phase 4: UX

- Build builder UI flows for graph authoring, execution, and inspection.
- Add real-time streaming output and tool trace visualization.

## Phase 5: Governance

- Add contract evolution governance and compatibility testing.
- Add policy bundles for tenant-level controls and approval workflows.
- Add release/version governance for tools and model adapters.
