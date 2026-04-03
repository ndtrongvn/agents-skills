---
name: rb-idea
description: File-gated design grilling skill that interrogates plans one question at a time using the latest rb-audit capsule to minimize hallucination and contract drift.
---

# RB Idea

Use this skill to stress-test and refine plans/designs with strict branch-by-branch questioning.

## Hard Gate (Mandatory)

Load and validate `$(pwd)/.agents/docs/rb-audit-latest.json` before asking any design question.

Required top-level fields:
- `v`
- `generated_at`
- `project_brief`
- `contracts_brief`
- `risk_brief`
- `rb_score`
- `action_queue`

Freshness rule:
- If stale/missing/invalid, stop and return one deterministic failure:
  - `RBIDEA_ERR_AUDIT_MISSING: Run /rb-audit to generate .agents/docs/rb-audit-latest.json.`
  - `RBIDEA_ERR_AUDIT_INVALID: rb-audit capsule schema is invalid; rerun /rb-audit.`

## Interview Behavior

1. Ask exactly one question at a time.
2. Resolve the current decision branch before moving to the next branch.
3. For every question, provide a recommended answer.
4. If a question can be answered from codebase facts, inspect codebase first instead of asking.
5. Validate each user answer against audit capsule + codebase facts.
6. If conflict is detected, surface mismatch and ask a correction question immediately.
7. Do not propose contracts/flows that contradict capsule facts.

## Question Order

Follow this sequence strictly:
1. Goals and success criteria
2. Constraints and non-goals
3. Architecture decisions
4. Interfaces and contracts
5. Rollout and testing

## Stop Condition

Finish only when unresolved critical decisions are zero.

## Output Style

For each turn:
- `Question:` one question only
- `Recommended answer:` concise recommendation
- `Why:` short reason tied to audit capsule/codebase fact
- `Status:` `open` or `resolved`
