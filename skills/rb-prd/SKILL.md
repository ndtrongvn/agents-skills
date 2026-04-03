---
name: rb-prd
description: Create a PRD from rb-idea output by interviewing the user, exploring the codebase, and locking implementation/testing decisions. Reads qa-ideas.md and writes qa-requirements.md in .agents/tasks.
---

This skill is invoked when the user wants a PRD for a feature/refactor initiative.

## File-Gated Inputs and Outputs

- Required input: `$(pwd)/.agents/tasks/qa-ideas.md` (generated from `/rb-idea`).
- Required output: $(pwd)/.agents/tasks/qa-requirements.md`.
- If input file is missing, stop and return:
  - `RBPRD_ERR_IDEAS_MISSING: Run /rb-idea and ensure .agents/tasks/qa-ideas.md exists.`

## Workflow

You may skip steps only when they are already fully resolved in `qa-ideas.md` and codebase facts.

1. Read `qa-ideas.md` first.
- Extract goals, constraints, unresolved questions, risks, and proposed directions.

2. Explore the repo.
- Verify all assertions in `qa-ideas.md`.
- Identify affected modules, contracts, data model, and operational constraints.
- If an answer is discoverable from codebase facts, discover it before asking.

3. Interview the user relentlessly until shared understanding.
- Ask questions one at a time.
- Walk every branch of the decision tree.
- Resolve dependencies between decisions before moving on.
- For each question, provide your recommended answer.

4. Design modules.
- Sketch major modules to build/modify.
- Prefer deep modules with simple, stable, testable interfaces.
- Check module boundaries and responsibilities with the user.
- Confirm which modules require tests.

5. Write the PRD using the template below.
- Use user-facing language where appropriate.
- Convert unresolved choices into explicit assumptions or out-of-scope notes.
- Save final result to `$(pwd)/.agents/tasks/qa-requirements.md`.

## PRD Template

## Problem Statement

The problem that the user is facing, from the user's perspective.

## Solution

The solution to the problem, from the user's perspective.

## User Stories

A LONG, numbered list of user stories. Each user story should be in the format of:

1. As an <actor>, I want a <feature>, so that <benefit>

Example:
1. As a mobile bank customer, I want to see balance on my accounts, so that I can make better informed decisions about my spending.

This list must be extremely extensive and cover all aspects of the feature.

## Implementation Decisions

A list of implementation decisions that were made. This can include:

- Modules that will be built/modified
- Interfaces of modules that will be modified
- Technical clarifications from the developer
- Architectural decisions
- Schema changes
- API contracts
- Specific interactions

Do NOT include specific file paths or code snippets.

## Testing Decisions

A list of testing decisions that were made. Include:

- What makes a good test (test external behavior, not implementation details)
- Which modules will be tested
- Prior art for tests (similar test styles already in the codebase)

## Out of Scope

A description of what is out of scope for this PRD.

## Further Notes

Any further notes about the feature.

## Quality Bar

Before saving `qa-requirements.md`, ensure:

- All critical decisions are resolved or recorded as explicit assumptions.
- User stories cover happy path, failure modes, permissions, observability, migration/rollout, and UX states.
- Implementation decisions are consistent with codebase and `qa-ideas.md` context.
- Testing decisions are specific enough to guide implementation.
