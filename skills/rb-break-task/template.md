# RB Break Task Templates

Use this file as the canonical template source for `rb-break-task`.

## 1) Task File Template (`task-{slug}.md`)

# Title: <Task title>

## Type

`AFK` or `HITL`

## Blocked by

- `None - can start immediately`

or

- `task-<other-task>.md`

## User stories addressed

- User story <number>
- User story <number>

## What to build

Concise end-to-end vertical-slice outcome.

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Notes

Optional execution notes without file paths or code snippets.

## 2) Task Index Template (`task-index.md`)

# Task Index

> Source PRD: $(pwd)/.agents/tasks/qa-requirements.md`

## Status Summary

- `todo`: <count>
- `in_progress`: <count>
- `done`: <count>
- `blocked`: <count>

## Ordered Tasks (dependency order)

1. `task-<slug>.md`  
   Title: <title>  
   Status: `todo | in_progress | done | blocked`  
   Type: `AFK | HITL`  
   Blocked by: <none or task list>

(repeat)

## Dependency Conflict Notes

- `None`

or list detected conflicts that require user resolution.

## 3) Execution Checklist (per task)

## 0) Pre-Flight Gates

- [ ] Dependency gate: all `Blocked by` tasks are `done`.
- [ ] Context gate: latest $(pwd)/.agents/docs/rb-audit-latest.json` is present and not stale.
- [ ] Contract gate: API/schema/interface assumptions are still valid.
- [ ] Scope gate: task maps to `qa-requirements.md` user stories.

## 1) TDD First

- [ ] Write/identify failing test(s) for external behavior.
- [ ] Confirm failure is real and scoped.
- [ ] Record test intent.

## 2) Implement Minimal Slice

- [ ] Implement smallest end-to-end change to satisfy tests.
- [ ] Keep slice complete and demoable.
- [ ] Avoid unrelated refactors.

## 3) Refactor Safely

- [ ] Refactor only after tests pass.
- [ ] Preserve behavior/interfaces.

## 4) Verify Before Done

- [ ] Run focused tests.
- [ ] Run required quality checks.
- [ ] Re-run task acceptance checklist.

## 5) Update Tracking

- [ ] Update task acceptance checkboxes.
- [ ] Update $(pwd)/.agents/tasks/task-index.md` status/notes.
- [ ] Log newly discovered dependency/risk.

## 6) Definition of Done

- [ ] Behavior works end-to-end for mapped stories.
- [ ] Tests pass for external behavior.
- [ ] No known blocker remains.
- [ ] Contract/doc updates done if interfaces changed.
- [ ] Rollback/feature-flag strategy documented for risky changes.
