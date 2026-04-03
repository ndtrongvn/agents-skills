---
name: rb-agent-md
description: Maintain an up-to-date root AGENTS.md using a reusable placeholder template with bidirectional distill/render/sync modes to reduce hallucination and doc drift.
---

# RB Agent MD

Create and maintain a reliable AGENTS standard by syncing between root `AGENTS.md` and this skill's `template.md`.

## Ownership

- Skill files owned here:
  - `.agents/skills/rb-agent-md/SKILL.md`
  - `.agents/skills/rb-agent-md/template.md`
- Runtime output target when requested:
  - root `AGENTS.md`

## Modes

### 1) `distill`

Purpose:
- Read root `AGENTS.md`
- Convert project-specific content into placeholder-driven reusable template
- Update `.agents/skills/rb-agent-md/template.md`

Rules:
- Preserve required section structure.
- Replace project details with angle placeholders.
- Do not remove anti-hallucination/source-priority policy.

### 2) `render`

Purpose:
- Read `.agents/skills/rb-agent-md/template.md`
- Resolve placeholders from current project facts
- Write updated root `AGENTS.md`

Fact resolution order (strict):
1. `.agents/docs`
2. `.agents/apis`
3. repository manifests/config/code (`package.json`, scripts, tests)
4. Context7 (if framework/library details are uncertain)
5. web search fallback only if unresolved

Rules:
- Prefer local truth over memory.
- Preserve required AGENTS sections even with partial data.
- Leave unresolved placeholders explicit; never invent facts.
- Add short provenance notes for resolved sections (source tier only, concise).
- If sources conflict, choose conservative/local value and add a conflict note.

### 3) `sync`

Purpose:
- Render expected AGENTS from template + current facts
- Compare with root `AGENTS.md`
- Report drift and recommended edits

Must detect:
- missing required sections
- stale/missing commands vs `package.json`
- broken source-priority policy
- accidental workflow-chain mandates (should not be enforced here)

## Required Placeholder Contract

Use angle-bracket tokens in template (canonical set):

- `<PROJECT_NAME>`
- `<PROJECT_SUMMARY>`
- `<CORE_STACK>`
- `<KNOWLEDGE_SOURCE_PRIORITY>`
- `<BUILD_COMMANDS>`
- `<TEST_COMMANDS>`
- `<CODE_STYLE_GUIDELINES>`
- `<TESTING_INSTRUCTIONS>`
- `<SECURITY_CONSIDERATIONS>`
- `<CURRENT_SYSTEM_DESIGN>`

You may add project-safe extension tokens when needed, but never remove these required tokens.

## Required AGENTS Section Set

Rendered `AGENTS.md` must contain at minimum:
- Knowledge source priority
- Project overview
- Build and test commands
- Code style guidelines
- Testing instructions
- Security considerations

Optional project sections can be added, but do not force any fixed skill-chain workflow.

## Anti-Hallucination Policy

- Never generate AGENTS content from memory alone.
- Always attempt local-source extraction first.
- Mark ambiguity explicitly when unresolved.
- Prefer stable, verifiable, low-assumption wording.

## Output Expectations

### Distill output
- Updated `template.md` with placeholders and stable structure.

### Render output
- Updated root `AGENTS.md` with resolved project facts.

### Sync output
- Drift report with:
  - missing sections
  - command mismatches
  - placeholder leaks
  - policy conflicts
  - recommended fix list
