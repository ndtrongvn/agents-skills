# agents-skills

Open-source custom agent skills focused on deterministic workflows, anti-hallucination guardrails, and execution handoffs for Codex-style development.

Repository: `https://github.com/ndtrongvn/agents-skills`

## What This Repository Provides

- Reusable `rb-*` skills with file-gated contracts
- A practical chain from audit to implementation readiness
- Project-ready root folders that map directly to `.agents/*` runtime locations

## Included Skills

| Skill | Purpose |
| --- | --- |
| `rb-audit` | Generate a compact repository truth capsule (`rb-audit-latest.json`) for downstream skills. |
| `rb-idea` | Interrogate and refine design decisions one question at a time using the latest audit capsule. |
| `rb-prd` | Convert validated ideas into an implementation-ready PRD artifact. |
| `rb-break-task` | Split PRD requirements into independent task files plus dependency-aware index tracking. |
| `rb-tdd` | Enforce behavior-first red-green-refactor implementation loops. |
| `rb-agent-md` | Keep root `AGENTS.md` synchronized from a placeholder-driven template. |

## Install For Codex

Example command (from `skill-installer` usage):

```bash
$skill-installer install https://github.com/ndtrongvn/agents-skills/tree/main/skills/rb-audit
```

For this repository's custom skills, copy or sync this repo's `skills/` content into your target project's `.agents/skills/` so each skill folder is available at runtime.

## Suggested Usage

Recommended chaining order:

`rb-audit > rb-idea > rb-prd > rb-break-task > rb-tdd`

Other usage:

- Keep root `AGENTS.md` up to date with `rb-agent-md`.

## Repository Layout

```text
.
|- apis/
|- docs/
|- skills/
|- tasks/
|- CONTRIBUTING.md
|- LICENSE
`- README.md
```

Root-to-runtime mapping for real projects:

- `apis/ -> .agents/apis/`
- `docs/ -> .agents/docs/`
- `skills/ -> .agents/skills/`
- `tasks/ -> .agents/tasks/`

## Folder Responsibilities

- `apis/`: API/interface contracts and integration-facing documentation consumed by agents.
- `docs/`: Generated chain artifacts, audit capsules, and planning/handoff documents.
- `skills/`: Source-of-truth skill definitions (`SKILL.md`) with optional templates/references/scripts.
- `tasks/`: Execution-ready artifacts such as idea docs, requirements, task index, and task slices.

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](./CONTRIBUTING.md).

## License

MIT. See [LICENSE](./LICENSE).
