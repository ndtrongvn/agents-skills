---
name: rb-audit
description: Repository audit skill that force-refreshes project truth into a compact anti-hallucination capsule for downstream skills.
---

# RB Audit

Run this skill first in every new session, and rerun it after major file changes.

## Objective

Produce a minimal, deterministic project brief capsule that downstream skills can reuse immediately.

- Write canonical output to `$(pwd)/.agents/docs/rb-audit-latest.json`.
- Also print the same compact JSON capsule to stdout.

## Protocol

1. Index repository context:
- `app/`, `components/`, `lib/`, `supabase/`, `tests/`
- include root `AGENTS.md` and `package.json`

2. Sync exact dependency versions:
- run `pnpm list --json`
- extract `next`, `@solana/kit`, `@supabase/supabase-js`

3. Run boundary and architecture checks:
- Next.js client/server boundaries (`"use client"` vs server files)
- API route and exported contract surface summary

4. Run full audit coverage:
- Solana and secret safety checks
- RLS/privilege boundary checks (Supabase SQL + service-role usage)
- API contract drift checks (unsafe JSON shape assumptions)
- Job durability/SSE lifecycle checks
- Test coverage gap checks for critical orchestration and API surfaces

5. Emit compact Project Brief Capsule:
- `v`
- `generated_at`
- `expires_at`
- `project_brief`
- `contracts_brief`
- `risk_brief` (top capped findings)
- `rb_score`
- `action_queue` (P0/P1 fix intents)

## Output Contract

The engine must produce one deterministic JSON object:

```json
{
  "v": "1.2.0",
  "generated_at": "2026-04-03T12:00:00Z",
  "expires_at": "2026-04-03T18:00:00Z",
  "project_brief": {},
  "contracts_brief": {},
  "risk_brief": {
    "counts": {},
    "top": []
  },
  "rb_score": {},
  "action_queue": {
    "p0": [],
    "p1": []
  }
}
```

Freshness policy:
- Capsule TTL is 6 hours from `generated_at`.

## Downstream Reuse Rule (Mandatory)

Downstream skills must consume `project_brief`, `contracts_brief`, and `risk_brief` first.

- Do not invent or mutate contracts/flows that contradict capsule facts.
- If contradiction is required or capsule is stale, rerun `rb-audit` first.
