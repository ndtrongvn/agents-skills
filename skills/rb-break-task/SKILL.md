---
name: rb-break-task
description: Break qa-requirements.md into independent tracer-bullet local task files (task-{slug}.md) and maintain task-index.md with dependency order and status tracking.
---

# RB Break Task

Convert PRD requirements into independently grabbable vertical-slice task files stored locally.

## Canonical Template Source

- Use `$(pwd)/.agents/skills/rb-break-task/template.md` as the single persistent template/rules source.
- Do not store persistent guidance docs inside `$(pwd)/.agents/tasks`.
- `$(pwd)/.agents/tasks` must contain only incoming/generated working artifacts (PRD, index, and task files).

## File-Gated Contract

- Required input: `$(pwd)/.agents/tasks/qa-requirements.md`
- Required outputs:
  - `$(pwd)/.agents/tasks/task-index.md`
  - `$(pwd)/.agents/tasks/task-{kebab-case-short-title}.md` (multiple files)

If input file is missing, stop and return exactly:
- `RBBREAK_ERR_PRD_MISSING: Run /rb-prd and ensure $(pwd)/.agents/tasks/qa-requirements.md exists.`

## Process

1. Load `$(pwd)/.agents/tasks/qa-requirements.md`.
- Extract problem and solution boundaries, user stories, implementation/testing decisions, and constraints.

2. Explore the codebase.
- Validate assumptions and integration boundaries before slicing.

3. Draft tracer-bullet vertical slices.
- Prefer thin end-to-end slices that are independently verifiable.

4. Classify and link tasks.
- Assign `Type` (`AFK`/`HITL`), `Blocked by`, and `User stories addressed`.
- Keep dependencies consistent and acyclic.

5. Quiz and refine with user.
- Review granularity, dependency graph, and HITL/AFK labels.

6. Write outputs using [template.md](template.md).
- Generate task files + index in dependency order.

## Quality Rules

- Preserve PRD intent and story mapping coverage.
- No file paths or code snippets in generated task docs.
- Ensure all `Blocked by` references resolve to generated task filenames.
- Ensure status tracking exists in `$(pwd)/.agents/tasks/task-index.md` for every generated task.
- Ensure dependency graph is acyclic before finalizing.
