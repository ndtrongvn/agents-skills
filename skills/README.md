# skills

Source-of-truth custom skill definitions for this repository.

## Responsibility

- Define each skill contract in `SKILL.md`.
- Keep reusable templates/references/scripts colocated with the owning skill.
- Provide deterministic, file-gated workflow behavior for downstream use.

## Runtime Mapping

In a real project, this folder maps to:

`skills/ -> .agents/skills/`

## Catalog

- `rb-audit`: repository truth capsule generation and risk-focused audit.
- `rb-idea`: branch-by-branch ideation and decision interrogation using audit facts.
- `rb-prd`: PRD generation from validated ideas and codebase verification.
- `rb-break-task`: PRD-to-task slicing with dependency-aware task indexing.
- `rb-tdd`: behavior-first red-green-refactor implementation discipline.
- `rb-agent-md`: root `AGENTS.md` distill/render/sync maintenance.

## Notes

- Treat skill folders as source modules; update with care to preserve contracts.
- Runtime artifacts belong in `docs/`, `tasks/`, and `apis/`, not in this folder.
