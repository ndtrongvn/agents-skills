# apis

Canonical API/interface contracts and integration-facing documentation for agent execution.

## Responsibility

- Store agent-consumable API truth (contracts, schemas, request/response expectations, and integration notes).
- Reduce hallucination risk by making interface facts explicit and versionable.
- Keep content focused on public behavior and compatibility constraints.

## Runtime Mapping

In a real project, this folder maps to:

`apis/ -> .agents/apis/`

## Typical Contents

- Endpoint contracts
- Event and message schemas
- External provider integration notes
- Compatibility and change logs for interfaces
