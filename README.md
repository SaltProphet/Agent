# Agent Builder (Bootstrap)

This repository bootstraps the **non-negotiable interoperability foundation** for an agent builder app.

## Included in this scaffold

- Unified provider-agnostic request schema
- Capability descriptor + negotiation with auto-downgrade planning
- Adapter interface plus OpenAI-compatible/local and generic REST adapter stubs
- Unit tests for capability negotiation behavior

## Run tests

```bash
python -m unittest discover -s tests -p 'test_*.py'
```
